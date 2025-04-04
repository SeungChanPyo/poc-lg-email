from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
import uuid
import time

# 요청 모델 (코틀린 API와 유사한 형식)
class ImageOption(BaseModel):
    pageRange: Optional[List[int]]

class Image(BaseModel):
    format: str
    data: str # Base64 인코딩된 이미지 데이터
    name: str
    option: Optional[ImageOption]
    # tableOption: Optional[List[Any]] = []

class OCRRequest(BaseModel):
    version: str = "v2" # 기본값 설정
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4())) # 기본값으로 UUID 생성
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000)) # 기본값으로 현재 타임스탬프
    images: List[Image]
    details: Optional[str] = ""
    modelType: Optional[str] = "UNIVERSAL"

# 응답 모델 (예상되는 기본 구조)
class Word(BaseModel):
    text: str
    boundingBox: List[List[int]]

class Line(BaseModel):
    text: str
    boundingBox: List[List[int]]
    words: List[Word]

class PageResult(BaseModel):
    page: int
    lines: List[Line]
    # 필요한 경우 다른 필드 추가 가능 (예: confidence, language)

class OCRResponse(BaseModel):
    result: Optional[List[PageResult]] = None # 결과가 없을 수도 있음
    requestId: str
    error: Optional[Dict[str, Any]] = None # 오류 발생 시 정보 포함 