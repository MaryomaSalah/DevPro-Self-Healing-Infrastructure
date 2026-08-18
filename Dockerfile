FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    pidof \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    google-genai \
    psutil \
    rich \
    matplotlib

COPY . .

CMD ["python", "app.py"]
