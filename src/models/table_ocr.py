from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict
import uuid
import time

class TableOption(BaseModel):
    pageRange: List[int] = []
    tableClue: List[str] = []

class BaseImage(BaseModel):
    format: str
    data: str # Base64 인코딩된 이미지 데이터
    name: str
    tableOption: List[TableOption] = []

class TableOCRRequest(BaseModel):
    version: str = "v4" # 기본값 설정
    requestId: str = Field(default_factory=lambda: str(uuid.uuid4())) # 기본값으로 UUID 생성
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000)) # 기본값으로 현재 타임스탬프
    images: List[BaseImage]
    details: Optional[str] = ""