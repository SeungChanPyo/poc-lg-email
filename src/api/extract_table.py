from fastapi import APIRouter, UploadFile, File, Depends

# 의존성 주입 및 서비스 로직 임포트 경로 수정
from ..models.extract_table import TableRequest
from ..services.general_ocr_service import process_general_ocr, process_general_ocr_file

router = APIRouter(
    tags=["recognition-controller"]      # API 문서 그룹화 태그
)
# response_mode=OCRResponse 로 할 건지지

EXAMPLE_RESULT = {
    "result": [
        {
            "page" : 1,
            "key" : "임대인",
            "value" : "주식회사 LG",
            "bbox" : [440.140, 91.179, 496.568, 104.427]
        },
        {
            "page" : 1,
            "key" : "임차인",
            "value" : "(주)홍길동",
            "bbox" : [448.420, 111.579, 488.259, 124.827]
        }
    ], 
    "errcd" : "00"
}
@router.post("/document/extract_table")
async def extract_table_endpoint(request: TableRequest = Depends()):
    """
    extract_table API 
    """
    print("extract_table Called")
    # 서비스 계층의 함수를 호출하여 OCR 처리
    return EXAMPLE_RESULT
    # return await process_general_ocr(request)