FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir "numpy<2.0"
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

# تست ساده - فقط ببینیم بالا می‌آید یا نه
CMD ["python", "-c", "print('Backend starting...'); import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000)"]
