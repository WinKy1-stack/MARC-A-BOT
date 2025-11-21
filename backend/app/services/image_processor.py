import time
import logging
import uuid
from typing import Dict, Optional, List, Any

from app.config import Config
from app.services.base_ocr_service import BaseOCRService

logger = logging.getLogger(__name__)


class ImageProcessor(BaseOCRService):
    """Xử lý ảnh đơn lẻ với PaddleOCR / PaddleX pipeline"""

    def process_image(self, file_path: str, image_id: Optional[str] = None) -> Dict:
        """
        Xử lý ảnh đơn lẻ với PaddleOCR

        Args:
            file_path: Đường dẫn đến file ảnh
            image_id: Mã định danh ảnh (tùy chọn)

        Returns:
            Dictionary chứa kết quả OCR
        """
        start_time = time.time()

        if image_id is None:
            image_id = str(uuid.uuid4())

        result: Dict[str, Any] = {
            "status": "error",
            "image_id": image_id,
            "ocr_text": "",
            "markdown": "",
            "confidence": 0.0,
            "processing_time_ms": 0,
            "output_files": {},
            "layout_detected": False,
            "error": None,
        }

        try:
            # Đảm bảo pipeline đã sẵn sàng
            self._ensure_pipeline_ready()

            # Gọi inference (BaseOCRService đã wrap PaddleX / PaddleOCR)
            logger.info("Processing %s with PaddleOCR/PaddleX...", file_path)
            ocr_results = self.ocr_inference(file_path)

            logger.debug("Raw ocr_results type: %s", type(ocr_results))

            if not ocr_results:
                logger.warning("OCR returned None or empty result for %s", image_id)
                result["status"] = "success"
                result["error"] = "No content detected in file"
                return result

            # Thử lấy phần tử đầu tiên (một ảnh)
            try:
                first = ocr_results[0]
            except Exception as exc:  # IndexError / KeyError / TypeError
                logger.warning("Cannot index ocr_results[0]: %r", exc)
                result["status"] = "success"
                result["error"] = "Invalid OCR result structure"
                return result

            logger.debug("ocr_results[0] type: %s", type(first))

            extracted_text = ""
            confidence_scores: List[float] = []
            lines_processed = 0
            lines_with_text = 0

            # ============================================================
            # 1) Trường hợp dùng PaddleX pipeline (Result object có .json)
            #    Theo docs: mỗi kết quả có thuộc tính .json chứa dict
            #    với key 'res' -> 'rec_texts', 'rec_scores', ...
            # ============================================================
            if hasattr(first, "json"):
                logger.info("Detected PaddleX Result object (has .json).")
                try:
                    data = first.json  # dict, giống nội dung save_to_json()
                except Exception as exc:
                    logger.error("Error accessing result.json: %r", exc)
                    result["status"] = "success"
                    result["error"] = "Cannot parse OCR result json"
                    return result

                logger.debug("json keys: %s", list(data.keys()))
                res_dict = data.get("res", data)

                rec_texts = res_dict.get("rec_texts", [])
                rec_scores = res_dict.get("rec_scores", [])

                # Mặc định coi mỗi phần tử rec_texts là 1 dòng
                lines_processed = len(rec_texts)

                logger.info(
                    "PaddleX OCR returned %d text segments for %s",
                    lines_processed,
                    image_id,
                )

                for idx, (txt, score) in enumerate(zip(rec_texts, rec_scores)):
                    text_str = str(txt) if txt is not None else ""
                    text_str = text_str.strip()

                    if not text_str:
                        logger.debug("Segment %d: empty text, skip", idx)
                        continue

                    try:
                        conf_val = float(score)
                    except (TypeError, ValueError):
                        conf_val = 0.0

                    extracted_text += text_str + "\n"
                    confidence_scores.append(conf_val)
                    lines_with_text += 1

                    logger.debug(
                        "Segment %d: '%s...' (conf=%.3f)",
                        idx,
                        text_str[:50],
                        conf_val,
                    )

            # ============================================================
            # 2) Trường hợp cũ: PaddleOCR kiểu list 2D
            #    ocr_results[0] là list các line: [ [box, (text, conf)], ... ]
            # ============================================================
            elif isinstance(first, (list, tuple)):
                logger.info(
                    "Detected classic PaddleOCR list result, falling back to old parser."
                )
                lines = first
                lines_processed = len(lines)
                logger.info(
                    "Processing %d OCR result lines for %s",
                    lines_processed,
                    image_id,
                )

                for idx, line in enumerate(lines):
                    if not line or not isinstance(line, (list, tuple)) or len(line) < 2:
                        logger.debug("Line %d: invalid structure, skip", idx)
                        continue

                    text_info = line[1]
                    if not text_info or not isinstance(text_info, (list, tuple)) or len(text_info) < 2:
                        logger.debug("Line %d: invalid text_info, skip", idx)
                        continue

                    try:
                        text = str(text_info[0]) if text_info[0] else ""
                        conf = float(text_info[1]) if text_info[1] is not None else 0.0
                    except (TypeError, ValueError, IndexError) as exc:
                        logger.warning("Line %d: error parsing text_info: %r", idx, exc)
                        continue

                    if text.strip():
                        extracted_text += text.strip() + "\n"
                        confidence_scores.append(conf)
                        lines_with_text += 1
                        logger.debug(
                            "Line %d: '%s...' (conf=%.3f)",
                            idx,
                            text[:50],
                            conf,
                        )
                    else:
                        logger.debug(
                            "Line %d: empty text after strip (conf=%.3f)", idx, conf
                        )

            else:
                # Không thuộc 2 dạng trên -> không biết parse
                logger.warning(
                    "Unexpected ocr_results[0] type: %s, cannot parse.",
                    type(first),
                )
                result["status"] = "success"
                result["error"] = "Unsupported OCR result format"
                return result

            logger.info(
                "Processed %d segments, extracted text from %d segments",
                lines_processed,
                lines_with_text,
            )

            # Tính độ tự tin trung bình
            confidence = (
                sum(confidence_scores) / len(confidence_scores)
                if confidence_scores
                else 0.0
            )

            # Nếu vẫn không có text
            if not extracted_text.strip():
                logger.warning("No text extracted from image %s", image_id)
                logger.warning(
                    "Total segments processed: %d, segments with text: %d",
                    lines_processed,
                    lines_with_text,
                )

                # Nếu có .json thì log mẫu ra cho debug
                if hasattr(first, "json"):
                    try:
                        logger.warning(
                            "Sample json['res'] keys: %s",
                            list(first.json.get("res", {}).keys()),
                        )
                    except Exception:
                        logger.warning("Cannot inspect json structure for debugging")

                result["status"] = "success"
                result["error"] = "No text content found in image"
                return result

            # Lưu output ra JSON nếu bật
            output_paths: Dict[str, str] = {}
            if Config.ENABLE_JSON_OUTPUT:
                import json
                output_dir = Config.OUTPUT_FOLDER / image_id
                output_dir.mkdir(exist_ok=True, parents=True)
                json_path = output_dir / "result.json"

                with open(json_path, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "text": extracted_text.strip(),
                            "confidence": confidence,
                            "lines_processed": lines_processed,
                            "lines_with_text": lines_with_text,
                        },
                        f,
                        ensure_ascii=False,
                        indent=2,
                    )

                output_paths["json"] = str(json_path)

            # Cập nhật kết quả cuối
            result.update(
                {
                    "status": "success",
                    "ocr_text": extracted_text.strip(),
                    "markdown": "",  # Standard OCR chưa cần markdown
                    "confidence": round(confidence, 4),
                    "processing_time_ms": int((time.time() - start_time) * 1000),
                    "output_files": output_paths,
                    "layout_detected": False,
                }
            )

            # Update last used time cho BaseOCRService (giữ pipeline warm)
            self._update_last_used()

            logger.info(
                "OCR completed for %s: confidence=%.2f, time=%dms",
                image_id,
                confidence,
                result["processing_time_ms"],
            )

        except Exception as e:  # noqa: BLE001
            logger.error("OCR processing error for %s: %s", image_id, e, exc_info=True)
            result["error"] = str(e)
            result["processing_time_ms"] = int((time.time() - start_time) * 1000)

        return result
