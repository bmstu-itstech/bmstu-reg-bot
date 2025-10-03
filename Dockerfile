FROM python:3.12-slim AS builder

WORKDIR /install

RUN apt-get update &&\
    apt-get install -y build-essential

COPY requirements.txt .

RUN pip install --upgrade pip &&\
    pip wheel --no-deps --wheel-dir /wheels -r requirements.txt

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV TZ=Europe/Moscow

WORKDIR /app

COPY --from=builder /wheels /wheels
COPY requirements.txt .

RUN pip install --no-deps --no-index --find-links=/wheels -r requirements.txt

COPY . .

ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]
