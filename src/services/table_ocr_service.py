from fastapi import HTTPException, UploadFile
import base64
from typing import Dict, Any

from ..core.rabbitmq import send_message_with_shared_reply
from ..models.table_ocr import TableOCRRequest
from ..core.config import DEFAULT_OCR_TIMEOUT

# General OCR 요청 큐 이름
TABLE_OCR_QUEUE = "recognition.pdf_table.requests"

async def process_table_ocr(request: TableOCRRequest):
    try:
        message = request.dict()
        result_data = await send_message_with_shared_reply(TABLE_OCR_QUEUE, message, timeout=DEFAULT_OCR_TIMEOUT)
        return result_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")
    