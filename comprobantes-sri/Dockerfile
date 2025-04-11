FROM python:3.13-slim-bullseye

WORKDIR /app
COPY . /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && pip install -r requirements.txt \
    && apt-get purge -y --auto-remove gcc python3-dev

COPY . .
