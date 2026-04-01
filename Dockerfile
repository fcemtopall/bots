FROM python:3.10-slim

WORKDIR /app

# Sistem bağımlılıkları (t3.small optimizasyonu)
RUN apt-get update && apt-get install -y gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Başlatma komutu
CMD ["python", "main.py"]