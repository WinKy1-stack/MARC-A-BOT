"""
Server-Sent Events (SSE) routes

Cung cap endpoint SSE de client nhan cap nhat trang thai xu ly theo thoi gian thuc.
"""
import json
import time
import random
import logging
from typing import Dict, Any, Generator

from flask import Blueprint, Response, stream_with_context

from app.ultis.request_queue import queue_manager

logger = logging.getLogger(__name__)

sse_bp = Blueprint('sse', __name__, url_prefix='/api/ocr')

_TIPS = [
    "Tip: Co gang giu file anh ro net de OCR chinh xac hon.",
    "Tip: PDF nhieu trang se mat thoi gian xu ly lau hon hinh don.",
    "Tip: Kiem tra lai huong xoay tai lieu truoc khi upload.",
    "Tip: Dung batch nho de giam thoi gian cho doi.",
    "Tip: Co the tai xuong ket qua JSON de xu ly tiep.",
]


def _sse_event(event: str, data: Dict[str, Any]) -> str:
    """Format du lieu theo SSE."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


@stream_with_context
def _status_stream(request_id: str) -> Generator[str, None, None]:
    """Sinh luong SSE lien tuc gui trang thai request."""
    yield _sse_event("connected", {"message": "SSE connected", "request_id": request_id})
    yield _sse_event("tip", {"message": random.choice(_TIPS)})

    while True:
        try:
            status = queue_manager.get_request_status(request_id)

            if status is None:
                yield _sse_event("error", {"message": "Request not found", "request_id": request_id})
                break

            state = status.get("status")
            payload = {
                "request_id": request_id,
                "status": state,
                "wait_time": status.get("wait_time"),
                "created_at": status.get("created_at"),
                "queue": queue_manager.get_queue_stats(),
            }

            # Include detailed progress info if available
            if status.get("progress_info"):
                payload["progress_info"] = status.get("progress_info")

            if state in ("completed", "failed", "timeout"):
                payload["result"] = status.get("result")
                payload["error"] = status.get("error")
                event_name = "completed" if state == "completed" else "error"
                yield _sse_event(event_name, payload)
                break

            yield _sse_event("update", payload)
            time.sleep(1.0)
        except GeneratorExit:
            logger.info("SSE client disconnected for request %s", request_id)
            break
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("SSE stream error for %s: %s", request_id, exc)
            yield _sse_event("error", {"message": str(exc), "request_id": request_id})
            break


@sse_bp.route('/stream/<request_id>', methods=['GET'])
def stream_request_status(request_id: str) -> Response:
    """
    SSE endpoint tra ve luong su kien trang thai cua request.
    Client lang nghe de cap nhat UI theo tien trinh backend.
    """
    return Response(_status_stream(request_id), mimetype='text/event-stream')

