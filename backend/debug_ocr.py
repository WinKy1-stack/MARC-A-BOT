"""
Script chẩn đoán chi tiết lỗi OCR
Giúp xác định nguyên nhân tại sao không extract được text
"""
import sys
import os
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.base_ocr_service import BaseOCRService
from paddleocr import PaddleOCR
import cv2
import numpy as np

# Setup logging với level DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_image_properties(image_path: str):
    """Kiểm tra thông tin ảnh"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA THÔNG TIN ẢNH")
    print("="*60)
    
    try:
        # Đọc ảnh bằng OpenCV
        img = cv2.imread(image_path)
        
        if img is None:
            print("❌ Không đọc được ảnh bằng OpenCV")
            return False
        
        print("✅ Đọc ảnh thành công")
        print(f"📐 Kích thước: {img.shape[1]}x{img.shape[0]} pixels")
        print(f"🎨 Channels: {img.shape[2] if len(img.shape) > 2 else 1}")
        print(f"📊 Data type: {img.dtype}")
        
        # Kiểm tra độ sáng trung bình
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        mean_brightness = np.mean(gray)
        print(f"💡 Độ sáng trung bình: {mean_brightness:.2f}/255")
        
        if mean_brightness < 30:
            print("⚠️  Ảnh quá tối - có thể ảnh hưởng OCR")
        elif mean_brightness > 225:
            print("⚠️  Ảnh quá sáng - có thể ảnh hưởng OCR")
        else:
            print("✅ Độ sáng phù hợp")
        
        # Kiểm tra độ tương phản
        std_brightness = np.std(gray)
        print(f"📈 Độ tương phản (std): {std_brightness:.2f}")
        
        if std_brightness < 20:
            print("⚠️  Độ tương phản thấp - text có thể khó phát hiện")
        else:
            print("✅ Độ tương phản tốt")
        
        return True
        
    except (IOError, OSError) as e:
        print(f"❌ Lỗi khi kiểm tra ảnh: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ocr_raw(image_path: str):
    """Test OCR trực tiếp với PaddleOCR"""
    print("\n" + "="*60)
    print("🔬 TEST OCR TRỰC TIẾP")
    print("="*60)
    
    try:
        # Khởi tạo PaddleOCR với các mức threshold khác nhau
        thresholds = [
            (0.1, 0.2, "Rất thấp - phát hiện mọi thứ"),
            (0.2, 0.3, "Thấp - được khuyến nghị"),
            (0.3, 0.5, "Trung bình - mặc định cũ"),
            (0.5, 0.6, "Cao - chỉ text rõ ràng")
        ]
        
        for det_thresh, box_thresh, desc in thresholds:
            print("\n" + "─"*60)
            print(f"🎯 Threshold: det={det_thresh}, box={box_thresh} ({desc})")
            print("─"*60)
            
            try:
                ocr = PaddleOCR(
                    device='cpu',  # Dùng CPU để tránh lỗi GPU
                    use_angle_cls=True,
                    lang='en',
                    det_db_thresh=det_thresh,
                    det_db_box_thresh=box_thresh,
                    rec_batch_num=6
                )
                
                # Chạy OCR
                result = ocr.ocr(image_path, cls=True)
                
                # Phân tích kết quả
                print(f"📦 Type of result: {type(result)}")
                print(f"📦 Length of result: {len(result) if result else 0}")
                
                if not result or len(result) == 0 or not result[0]:
                    print("❌ Kết quả OCR rỗng hoặc None")
                elif len(result[0]) == 0:
                    print("❌ Không phát hiện text nào")
                else:
                    print(f"📄 Number of lines detected: {len(result[0])}")
                    print(f"\n📝 Chi tiết {min(3, len(result[0]))} dòng đầu tiên:")
                    
                    for idx, line in enumerate(result[0][:3]):
                        print(f"\n  Line {idx + 1}:")
                        print(f"    Structure: {type(line)}")
                        print(f"    Length: {len(line) if isinstance(line, (list, tuple)) else 'N/A'}")
                        
                        if isinstance(line, (list, tuple)) and len(line) >= 2:
                            box = line[0]
                            text_info = line[1]
                            
                            print(f"    Box coords: {box}")
                            print(f"    Text info type: {type(text_info)}")
                            
                            if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                text = text_info[0]
                                conf = text_info[1]
                                print(f"    ✅ Text: '{text}'")
                                print(f"    ✅ Confidence: {conf:.3f}")
                            else:
                                print(f"    ❌ Invalid text_info structure: {text_info}")
                        else:
                            print(f"    ❌ Invalid line structure: {line}")
                    
                    # Tổng hợp text
                    all_text = []
                    for line in result[0]:
                        if isinstance(line, (list, tuple)) and len(line) >= 2:
                            text_info = line[1]
                            if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                text = str(text_info[0])
                                if text.strip():
                                    all_text.append(text)
                    
                    if all_text:
                        print(f"\n✅ TỔNG HỢP TEXT ({len(all_text)} dòng):")
                        print("─" * 60)
                        print("\n".join(all_text[:10]))
                        if len(all_text) > 10:
                            print(f"\n... và {len(all_text) - 10} dòng nữa")
                    else:
                        print("\n❌ Không có text hợp lệ sau khi parse")
                
                # Cleanup
                del ocr
                
            except (RuntimeError, ValueError, OSError) as e:
                print(f"❌ Lỗi với threshold này: {e}")
                continue
        
    except (RuntimeError, ValueError, OSError) as e:
        print(f"❌ Lỗi test OCR: {e}")
        import traceback
        traceback.print_exc()


def test_with_service(image_path: str):
    """Test với BaseOCRService"""
    print("\n" + "="*60)
    print("🔧 TEST VỚI BASE OCR SERVICE")
    print("="*60)
    
    try:
        service = BaseOCRService()
        
        print("⏳ Đang xử lý với OCR service...")
        result = service.ocr_inference(image_path)
        
        print(f"\n📦 Result type: {type(result)}")
        print(f"📦 Result length: {len(result) if result else 0}")
        
        if not result or not result[0]:
            print("❌ Service trả về kết quả rỗng")
        elif len(result[0]) == 0:
            print("❌ Service không phát hiện text")
        else:
            print(f"📄 Lines detected: {len(result[0])}")
            print("\n✅ Service có phát hiện text!")
            print(f"   Ví dụ dòng đầu tiên: {result[0][0]}")
        
    except (RuntimeError, ValueError, OSError) as e:
        print(f"❌ Lỗi test service: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("\n❌ Usage: python debug_ocr.py <path_to_image>")
        print("\nExample:")
        print("  python debug_ocr.py image.jpg")
        print("  python debug_ocr.py C:/path/to/image.png")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print("\n" + "="*60)
    print("🔍 CHẨN ĐOÁN CHI TIẾT LỖI OCR")
    print("="*60)
    print(f"📁 File: {image_path}")
    print(f"📍 Absolute path: {os.path.abspath(image_path)}")
    print(f"✅ File exists: {os.path.exists(image_path)}")
    print(f"📊 File size: {os.path.getsize(image_path) / 1024:.2f} KB")
    
    if not os.path.exists(image_path):
        print("\n❌ File không tồn tại!")
        sys.exit(1)
    
    # 1. Kiểm tra thông tin ảnh
    if not check_image_properties(image_path):
        print("\n❌ Không thể đọc ảnh - dừng chẩn đoán")
        sys.exit(1)
    
    # 2. Test OCR trực tiếp với nhiều threshold
    test_ocr_raw(image_path)
    
    # 3. Test với service
    test_with_service(image_path)
    
    print("\n" + "="*60)
    print("🏁 HOÀN TẤT CHẨN ĐOÁN")
    print("="*60)
    print("\n💡 Khuyến nghị:")
    print("  - Nếu ảnh quá tối/sáng: Điều chỉnh độ sáng trước khi OCR")
    print("  - Nếu không detect được text: Thử giảm threshold xuống 0.1-0.2")
    print("  - Nếu ảnh có text xoay: Đảm bảo use_angle_cls=True")
    print("  - Nếu text quá nhỏ: Resize ảnh lên kích thước lớn hơn")


if __name__ == "__main__":
    main()
