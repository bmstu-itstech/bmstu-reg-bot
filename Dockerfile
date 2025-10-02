FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
COPY bot/ ./bot/
RUN mkdir -p ./data

RUN pip install --no-cache-dir -r requirements.txt

COPY .env .env

CMD ["python", "bot/main.py"]