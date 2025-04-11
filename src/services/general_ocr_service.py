from fastapi import HTTPException, UploadFile
import base64
from typing import Dict, Any

from ..core.rabbitmq import send_message_async, wait_for_message
from ..models.general_ocr import OCRRequest, BaseImage # 모델 임포트 경로 수정
from ..core.config import DEFAULT_OCR_TIMEOUT

# General OCR 요청 큐 이름
GENERAL_OCR_QUEUE = "recognition.general.requests"

async def process_general_ocr(request: OCRRequest):
    try:
        message = request.dict()
        correlation_id = await send_message_async(GENERAL_OCR_QUEUE, message)
        result_data = await wait_for_message(f"{GENERAL_OCR_QUEUE}.results", correlation_id, timeout=DEFAULT_OCR_TIMEOUT)
        return result_data
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")
    
    
async def process_general_ocr_file(file: UploadFile):
    try:
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode("utf-8")
        file_format = file.filename.split('.')[-1].lower()
        if file_format not in ['jpg', 'jpeg', 'png', 'bmp', 'pdf']:
            file_format = 'png' # 예시로 png 사용

        # OCRRequest 모델 생성
        # request_id, timestamp 등은 모델의 기본값 팩토리 사용
        ocr_request = OCRRequest(
            images=[
                BaseImage(
                    format=file_format,
                    data=image_base64,
                    name=file.filename,
                )
            ]
        )
        return await process_general_ocr(ocr_request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"General OCR 파일 처리 중 오류: {str(e)}")