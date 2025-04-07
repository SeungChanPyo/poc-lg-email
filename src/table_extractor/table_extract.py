import fitz
import camelot
import re
import io
import base64
from ..services.document_ocr_service import process_document_ocr
from ..models.document_ocr import DocumentOCRRequest
from typing import List, Dict, Any, Union, Optional

def convert_document_ocr_res(document_ocr_res, page_width, page_height):
    '''
    Document OCR 결과를 원하는 형태로 변환하는 함수
    key가 없을 경우 결과에 추가하지 않으며 pdf 페이지 크기로 bbox를 역 정규화화
    '''
    results = []
    for page_result in document_ocr_res.get("result", []):
        page_num = page_result.get("page", 1)
        fields = page_result.get("result", {})
        
        for key, field_info in fields.items():
            values = field_info.get("value", [])
            bboxes = field_info.get("box", [])
            
            if not values or not bboxes or not bboxes[0]:
                continue
            
            value = values[0]
            box = bboxes[0]
            
            x1 = box[0] * page_width
            y1 = box[1] * page_height
            x2 = box[2] * page_width
            y2 = box[3] * page_height
            
            results.append({
                "page": page_num,
                "key" : key,
                "value": value.strip(),
                "bbox": [x1,y1,x2,y2]
            })
    return results
            
def create_request(page) ->DocumentOCRRequest:
    '''
    DocumentOCRRequest 객체를 만들기 위한 함수
    계약서 샘플에 해당하는 템플릿 ID로 하드코딩해놓음 -> 수정 필요요
    '''
    page_pdf = fitz.open()
    page_pdf.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
    pdf_bytes = page_pdf.write()
    page_pdf.close()
    
    doc_request = {
        "version" : "v4",
        "requestId" : "1131_60000549",
        "timestamp" : 0,
        "images": [
            {
            "format" : "pdf",
            "data" : base64.b64encode(pdf_bytes).decode("utf-8"),
            "name" : "page.pdf"
        }
        ],
        "ocrType": "EDEN",
        "details": "pdf_text_extract=img",
        "recognitionId": 0,
        "templateName": "",
        "modelType": "UNIVERSAL"
    }
    doc_request = DocumentOCRRequest(**doc_request)
    return doc_request

def check_contract_condition(text) -> bool:
    """
    사전 학습한 DocumentModel에 해당하는 페이지인지 찾는 함수
    제 1 조 (계약의 일반조건)이 존재하면 True를 리턴턴
    """
    contract_pattern = re.compile(r"제\s*\d+\s*조.*계약의\s*일반\s*조건")
    if contract_pattern.search(text):
        return True

async def pdf_table_extract(pdf_object):
    '''
    PDF Object로 부터 원하는 Key, value를 추출하는 함수수
    '''
    doc = fitz.open(stream=pdf_object.read(), filetype="pdf")
    pdf_object.seek(0)  # 파일 포인터 리셋
    results = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        page_width = page.rect.width
        page_height = page.rect.height
        text = page.get_text()
        # print("text :", text)
        if check_contract_condition(text):
            request = create_request(page)
            document_ocr_res = await process_document_ocr(request)
            converted_document_ocr_res = convert_document_ocr_res(document_ocr_res, page_width, page_height)
            results.extend(converted_document_ocr_res)
    return results     