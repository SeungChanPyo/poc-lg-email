from fastapi import HTTPException, UploadFile
import base64
from typing import Dict, Any

from ..core.rabbitmq import send_message, poll_result
from ..models.general_ocr import OCRRequest, Image # 모델 임포트 경로 수정
from ..core.config import DEFAULT_OCR_TIMEOUT

# General OCR 요청 큐 이름
GENERAL_OCR_QUEUE = "recognition.general.requests"

async def process_general_ocr(request: OCRRequest):
    """General OCR 요청을 처리하고 결과를 반환합니다."""
    try:
        # Pydantic 모델을 dict로 변환하여 메시지 생성
        message = request.dict()
        # print("message :", message)

        # RabbitMQ에 메시지 전송
        correlation_id = send_message(GENERAL_OCR_QUEUE, message)
        print("correlation_id :", correlation_id)

        # 결과 폴링
        # API 타임아웃보다 약간 짧게 내부 타임아웃 설정 가능
        result_data = poll_result(GENERAL_OCR_QUEUE, correlation_id, timeout=DEFAULT_OCR_TIMEOUT)
        print("result_data :", result_data)

        # 결과 데이터 검증 및 OCRResponse 모델로 변환
        # 엔진 응답 형식에 따라 적절히 파싱해야 함
        if not result_data or ('error' in result_data and result_data['error']):
             print(f"OCR 엔진 오류 응답: {result_data}")
             # 엔진에서 에러를 명시적으로 반환하는 경우
             error_info = result_data.get('error', {'code': 500, 'message': 'OCR 엔진 처리 실패 (상세 정보 없음)'})
             raise HTTPException(status_code=error_info.get('code', 500), detail=error_info.get('message', 'OCR 엔진 오류'))
        elif 'result' not in result_data:
             print(f"OCR 엔진 응답 형식 오류: 'result' 필드 누락. 응답: {result_data}")
             raise HTTPException(status_code=500, detail="OCR 엔진 응답 형식 오류 ('result' 필드 누락)")

        # OCRResponse 모델로 응답 구성 (오류 필드는 None)
        # result_data가 OCRResponse 구조와 완벽히 일치하지 않을 수 있으므로, 필요한 필드만 추출하거나 변환
        # return OCRResponse(
        #     result=result_data.get('result'), # 엔진 응답의 'result' 부분을 사용
        #     requestId=result_data.get('requestId', request.requestId), # 엔진 응답의 requestId 우선 사용
        #     error=None
        # )
        return result_data

    except HTTPException as http_exc:
        print(f"HTTP Exception!! : {http_exc}")
        # 이미 HTTPException인 경우 그대로 다시 발생
        raise http_exc
    except Exception as e:
        # 기타 예외 처리
        print(f"General OCR 처리 중 오류 발생: {e}")
        raise HTTPException(status_code=500, detail=f"General OCR 처리 중 오류: {str(e)}")

async def process_general_ocr_file(file: UploadFile):
    """파일 업로드를 통한 General OCR 요청을 처리합니다."""
    # 파일 사이즈 제한 확인 (예: 10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE // 1024 // 1024}MB까지 허용됩니다.")

    # 파일 형식 확인 및 Base64 인코딩
    file_format = file.filename.split('.')[-1].lower()
    if file_format not in ['jpg', 'jpeg', 'png', 'bmp', 'pdf']:
        # 지원하지 않는 형식이거나 확장자가 없는 경우 기본값 또는 오류 처리
        # 여기서는 일단 jpg로 가정하거나, 특정 기본값 사용
        file_format = 'png' # 예시로 png 사용
        print(f"경고: 파일 확장자({file.filename.split('.')[-1]})가 명확하지 않거나 지원되지 않아 '{file_format}'으로 가정합니다.")

    image_base64 = base64.b64encode(contents).decode("utf-8")

    # OCRRequest 모델 생성
    # request_id, timestamp 등은 모델의 기본값 팩토리 사용
    ocr_request = OCRRequest(
        images=[
            Image(
                format=file_format,
                data=image_base64,
                name=file.filename,
                # 필요시 option, tableOption 추가
            )
        ]
        # version, requestId, timestamp, modelType 등은 기본값 사용
    )

    # 생성된 요청 객체로 기존 OCR 처리 함수 호출
    return await process_general_ocr(ocr_request) 