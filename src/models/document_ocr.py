from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
import uuid
import time

class BaseImage(BaseModel):
    format: str
    data: str # Base64 인코딩된 이미지 데이터
    name: str

class DocumentOCRRequest(BaseModel):
    version: str = "v4" # 기본값 설정
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4())) # 기본값으로 UUID 생성
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000)) # 기본값으로 현재 타임스탬프
    images: List[BaseImage]
    ocrType: str = "EDEN"
    details: Optional[str] = ""
    recognitionId: int = 0
    templateName: str = ""
    modelType: Optional[str] = "UNIVERSAL"
    
#     "ocrType": "string",
#   "details": "string",
#   "recognitionId": 0,
#   "templateName": "string",
    