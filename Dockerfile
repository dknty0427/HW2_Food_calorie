# 파이썬 3.11 슬림 이미지를 사용하여 이미지 크기를 최소화하고 보안성을 높입니다.
FROM python:3.11-slim

# 환경 변수 설정
# PYTHONDONTWRITEBYTECODE: 파이썬이 .pyc 파일을 쓰지 않도록 하여 불필요한 용량 감소 및 I/O 절약
# PYTHONUNBUFFERED: 로그가 버퍼링 없이 터미널에 즉시 출력되게 하여 컨테이너 로그 모니터링에 유리
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 변경 빈도가 낮은 요구사항(requirements) 파일을 먼저 복사하여, 소스 코드가 수정되어도 의존성 설치 단계를 캐시로 재활용할 수 있게 최적화
COPY requirements.txt .

# pip 업그레이드 및 패키지 설치
# --no-cache-dir 옵션으로 설치 파일 캐시를 남기지 않아 도커 이미지 크기 축소
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 나머지 소스 코드 전체 복사 (.dockerignore 파일을 나중에 추가하여 불필요한 파일 제외 권장)
COPY . .

# 보안 베스트 프랙티스: root 권한으로 애플리케이션을 실행하지 않도록 전용 사용자 생성 및 권한 부여
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser

# 외부에서 접근 가능한 포트 열기
EXPOSE 8000

# 서버 실행 명령 (0.0.0.0으로 띄워야 도커 포트 매핑 후 외부 접근이 가능)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
