FROM python:3.11-slim AS base

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=600 \
    PIP_RETRIES=20

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 600 --retries 20 -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]