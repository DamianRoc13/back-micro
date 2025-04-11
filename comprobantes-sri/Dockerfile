FROM python:3.12-alpine

RUN groupadd -r transcription_service && \
    useradd -r -g transcription_service -d /home/transcription_service transcription_service && \
    mkdir -p /home/transcription_service && \
    chown transcription_service:transcription_service /home/transcription_service
WORKDIR /app
RUN pip install --no-cache-dir poetry

RUN poetry config virtualenvs.create false --local

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --with transcription_service

RUN mkdir src && \
    chown -R transcription_service:transcription_service /app

USER transcription_service

