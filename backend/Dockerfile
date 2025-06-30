FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install \
      --no-cache-dir \
      --timeout 600 \          
      --retries 20 \           
      --progress-bar off \
      -r requirements.txt

COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]