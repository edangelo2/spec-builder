FROM python:3.11-slim AS base
# pip patience flags—same as other services
ENV PIP_NO_CACHE_DIR=1 \
    PIP_DEFAULT_TIMEOUT=600 \
    PIP_RETRIES=20

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 600 --retries 20 -r requirements.txt

COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]