FROM python:3.12-slim

WORKDIR /app

# نصب dependencies سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libgeos-dev \
    && rm -rf /var/lib/apt/lists/*

# نصب numpy سازگار با CPU قدیمی (بدون بهینه‌سازی x86-v2)
COPY requirements.txt .

# نصب numpy نسخه 1.26 (بدون مشکل CPU)
RUN pip install --no-cache-dir "numpy<2.0"

# سپس بقیه
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]