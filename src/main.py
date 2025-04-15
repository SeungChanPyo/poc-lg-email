from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 설정 및 API 라우터 임포트 경로 수정
from .core.config import API_HOST, API_PORT
from .core.rabbitmq import setup_result_consumer
from .api import ocr # api 폴더의 ocr 모듈 임포트
from .api import extract_table
# FastAPI 앱 생성
app = FastAPI(
    title="AI Center API Server",
    description="AI Center 엔진과 상호작용하는 API 서버",
    version="1.0.0"
)
SHARED_REPLY_QUEUE = "shared_reply_queue"

# CORS 설정 (모든 출처 허용 - 개발 환경)
# 운영 환경에서는 특정 출처만 허용하도록 수정 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(ocr.router) # OCR 관련 라우터 등록
app.include_router(extract_table.router)

# 루트 엔드포인트
@app.get("/")
def read_root():
    return {"message": "AI Center API 서버에 오신 것을 환영합니다."}

shared_consumer_connection = None
@app.on_event("startup")
async def startup_event():
    global shared_consumer_connection
    # 공유 응답 큐(SHARED_REPLY_QUEUE)에 대해 한 번 소비자를 설정합니다.
    shared_consumer_connection = await setup_result_consumer(SHARED_REPLY_QUEUE)
    print("공통 응답 소비자(central dispatcher)가 설정되었습니다.")
    
@app.on_event("shutdown")
async def shutdown_event():
    if shared_consumer_connection:
        await shared_consumer_connection.close()

# 서버 실행 (스크립트 직접 실행 시)
if __name__ == "__main__":
    # uvicorn.run 에 모듈 경로와 앱 객체 전달
    # reload=True는 개발 중에 코드 변경 시 자동 재시작 활성화
    uvicorn.run("src.main:app", host=API_HOST, port=API_PORT, reload=True) 