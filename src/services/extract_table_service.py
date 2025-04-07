from fastapi import HTTPException, UploadFile
import base64
from typing import Dict, Any
from ..table_extractor.table_extract import pdf_table_extract
import fitz


async def process_extract_table(request):
    filename = request.file.filename
    if not filename.lower().endswith(".pdf"):
        return {"result" : "", "errcd" : "02"}
    
    try:
        pdf_object = request.file.file
        result = await pdf_table_extract(pdf_object)
        return {"result" : result, "erred" : "00"}
    except:
        return {"result" : "", "errcd" : "03"}
    
    # print("request :", request)
    # try:
    #     pdf_doc = fitz.open(request)
    #     print("pdf_doc :", pdf_doc)
    #     return {"result" : "", "errcd" : "00"}
    # except:
    #     return {"result" : "", "errcd" : "02"}
    
# from ..core.rabbitmq import send_message, poll_result
# from ..models.general_ocr import OCRRequest, Image # 모델 임포트 경로 수정
# from ..core.config import DEFAULT_OCR_TIMEOUT
