FROM python:3.10-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    bash \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

CMD ["python", "example.py"]