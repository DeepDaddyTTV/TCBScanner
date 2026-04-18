FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    LIBRARY_DIR=/manga \
    WORK_DIR=/data/work

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /data/work /manga \
    && chown -R appuser:appuser /data /manga

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

USER appuser

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
