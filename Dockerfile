FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    docker \
    google-genai \
    psutil \
    rich \
    matplotlib

COPY . .

CMD ["python", "app.py"]