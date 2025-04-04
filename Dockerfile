# 1. 베이스 이미지 선택 (슬림 버전 사용)
FROM python:3.10-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 환경 변수 설정
# 파이썬 로그가 버퍼링 없이 즉시 출력되도록 설정
ENV PYTHONUNBUFFERED 1
# PYTHONPATH 설정 (src 폴더를 모듈 검색 경로에 추가)
ENV PYTHONPATH=/app

# 시스템 패키지 설치치
RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    poppler-utils \
    ghostscript \
    && rm -rf /var/lib/apt/lists/*

# 4. 의존성 파일 복사 및 설치
# requirements.txt만 먼저 복사하여 레이어 캐싱 활용
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 코드 복사
# src 디렉토리의 내용을 /app/src 로 복사
COPY ./src /app/src

# 6. 애플리케이션 실행 포트 노출
EXPOSE 8000

# 7. 애플리케이션 실행 명령
# uvicorn을 사용하여 src/main.py의 app 실행
# --reload 옵션 추가: 코드 변경 시 자동으로 서버 재시작
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"] 