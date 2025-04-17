from fastapi import HTTPException, UploadFile
import base64
from typing import Dict, Any

from ..core.rabbitmq import send_message_with_shared_reply
from ..models.document_ocr import DocumentOCRRequest # 모델 임포트 경로 수정
from ..core.config import DEFAULT_OCR_TIMEOUT

# General OCR 요청 큐 이름
DOCUMENT_OCR_QUEUE = "recognition.domain_document.requests"
DOCUMENT_BIZ_LICENCE_OCR_QUEUE = "recognition.biz_license.requests"
DOCUMENT_BIZ_CARD_OCR_QUEUE = "recognition.biz_card.requests"
DOCUMENT_ID_CARD_OCR_QUEUE = "recognition.id_card.requests"

async def process_document_ocr(request: DocumentOCRRequest):
    try:
        message = request.dict()
        result_data = await send_message_with_shared_reply(DOCUMENT_OCR_QUEUE, message, timeout=DEFAULT_OCR_TIMEOUT)
        return result_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")
    
async def process_biz_licence_ocr(request: DocumentOCRRequest):
    try:
        message = request.dict()
        result_data = await send_message_with_shared_reply(DOCUMENT_BIZ_LICENCE_OCR_QUEUE, message, timeout=DEFAULT_OCR_TIMEOUT)
        return result_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")
    
async def process_biz_card_ocr(request: DocumentOCRRequest):
    try:
        message = request.dict()
        result_data = await send_message_with_shared_reply(DOCUMENT_BIZ_CARD_OCR_QUEUE, message, timeout=DEFAULT_OCR_TIMEOUT)
        return result_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")
    
async def process_id_card_ocr(request: DocumentOCRRequest):
    try:
        message = request.dict()
        result_data = await send_message_with_shared_reply(DOCUMENT_ID_CARD_OCR_QUEUE, message, timeout=DEFAULT_OCR_TIMEOUT)
        return result_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")
    
    