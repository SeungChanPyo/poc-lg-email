import os
from dotenv import load_dotenv

load_dotenv() # .env 파일 로드

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", "5672") # 포트는 정수형으로 변환
RABBITMQ_USER = os.environ.get("RABBITMQ_USER", "dusrnth")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS", "eden123!")

# API 설정
API_HOST = os.environ.get("API_HOST")
API_PORT = os.environ.get("API_PORT")

# OCR 기본 타임아웃 (초)
DEFAULT_OCR_TIMEOUT = 60 