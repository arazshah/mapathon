FROM python:3.12-slim

WORKDIR /app

# نصب وابستگی‌های سیستمی
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    g++ \
    libgeos-dev \
    libgeos-c1v5 \
    libproj-dev \
    proj-bin \
    && rm -rf /var/lib/apt/lists/*

# ساخت پوشه دیتا برای پایداری SQLite
RUN mkdir -p /app/data

COPY requirements.txt .

# حذف کش pip و نصب اجباری numpy 1.26.4
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --force-reinstall numpy==1.26.4 && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
