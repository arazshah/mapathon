FROM python:3.12-slim

WORKDIR /app

# نصب dependencies سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# نصب numpy سازگار با CPU قدیمی (بدون بهینه‌سازی x86-v2)
COPY requirements.txt .

# نصب numpy نسخه 1.26 (بدون مشکل CPU)
RUN pip install --no-cache-dir "numpy<2.0"

# سپس بقیه dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ایجاد پوشه برای داده‌ها
RUN mkdir -p /app/data

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
