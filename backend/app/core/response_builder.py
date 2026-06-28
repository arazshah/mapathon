from typing import Any


def build_response(result: dict) -> dict:
    """
    ساخت پاسخ نهایی برای فرانت‌اند
    """
    return {
        "success": result.get("success", False),
        "type": result.get("type"),
        "message": result.get("message", ""),
        "data": result,
    }
