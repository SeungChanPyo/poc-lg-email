from fastapi import HTTPException, UploadFile
import base64
from typing import Dict, Any

from ..core.rabbitmq import send_message_async, wait_for_message
from ..models.document_ocr import DocumentOCRRequest # 모델 임포트 경로 수정
from ..core.config import DEFAULT_OCR_TIMEOUT

# General OCR 요청 큐 이름
DOCUMENT_OCR_QUEUE = "recognition.domain_document.requests"

async def process_document_ocr(request: DocumentOCRRequest):
    try:
        message = request.dict()
        correlation_id = await send_message_async(DOCUMENT_OCR_QUEUE, message)
        result_data = await wait_for_message(f"{DOCUMENT_OCR_QUEUE}.results", correlation_id, timeout=DEFAULT_OCR_TIMEOUT)
        return result_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")