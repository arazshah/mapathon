FROM python:3.12-slim

WORKDIR /app

# نصب dependencies سیستم + curl برای health check
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# نصب numpy نسخه 1.26 (بدون مشکل CPU)
RUN pip install --no-cache-dir "numpy<2.0"

# نصب بقیه dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/data

EXPOSE 8000

# Health check ساده با curl
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
