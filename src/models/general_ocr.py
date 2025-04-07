from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
import uuid
import time

# 요청 모델 (코틀린 API와 유사한 형식)
class ImageOption(BaseModel):
    pageRange: Optional[List[int]]

class BaseImage(BaseModel):
    format: str
    data: str # Base64 인코딩된 이미지 데이터
    name: str
    
class OptionImage(BaseImage):
    option: Optional[ImageOption]

class OCRRequest(BaseModel):
    version: str = "v2" # 기본값 설정
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4())) # 기본값으로 UUID 생성
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000)) # 기본값으로 현재 타임스탬프
    images: List[OptionImage]
    details: Optional[str] = ""
    modelType: Optional[str] = "UNIVERSAL"