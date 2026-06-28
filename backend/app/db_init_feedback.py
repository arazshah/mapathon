from app.core.database import init_db

if __name__ == "__main__":
    print("در حال ساخت جداول دیتابیس...")
    init_db()
    print("جداول با موفقیت ساخته شد.")
