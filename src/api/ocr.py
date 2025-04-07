from fastapi import APIRouter, UploadFile, File, Depends

# 의존성 주입 및 서비스 로직 임포트 경로 수정
from ..models.general_ocr import OCRRequest
from ..models.document_ocr import DocumentOCRRequest
from ..services.general_ocr_service import process_general_ocr, process_general_ocr_file
from ..services.document_ocr_service import process_document_ocr

router = APIRouter(
    tags=["recognition-controller"]      # API 문서 그룹화 태그
)
# response_mode=OCRResponse 로 할 건지지
@router.post("/document/general")
async def general_ocr_endpoint(request: OCRRequest):
    """
    GeneralOCR API - JSON 요청 본문을 사용하여 OCR을 수행합니다.
    엔진으로 이미지 데이터를 전송하고 인식 결과를 반환합니다.
    """
    print("General OCR Called")
    # 서비스 계층의 함수를 호출하여 OCR 처리
    return await process_general_ocr(request)

@router.post("/document/general/file")
async def general_ocr_file_endpoint(file: UploadFile = File(...)):
    """
    GeneralOCR API - 파일 업로드 방식으로 이미지를 처리합니다.
    업로드된 이미지 파일을 OCR 엔진으로 분석하여 결과를 반환합니다.
    """
    # 서비스 계층의 파일 처리 함수 호출
    return await process_general_ocr_file(file)

# @router.post("/domain-document")
# async def document_ocr_endpoint(request: DocumentOCRRequest):
#     return await process_document_ocr(request)

@router.post("/domain-document")
async def document_ocr_endpoint(
    domainId: int, 
    templateId: int, 
    ocrType: str, 
    request: DocumentOCRRequest
    ):
    request.requestId = f"{domainId}_{templateId}"
    request.ocrType = ocrType
    return await process_document_ocr(request)
    # request["requestId"]
    # return await process_document_ocr(request)
# 필요한 경우 여기에 다른 OCR 관련 엔드포인트 추가 가능 (예: Table OCR, Document OCR 등) 