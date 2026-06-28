import json
from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """
تو یک برنامه‌ریز GIS هوشمند برای شهر تهران هستی.
سوال کاربر را تحلیل کن و فقط یک JSON معتبر برگردان.

قوانین:
1. location_name فقط نام مکان خالص باشد (بدون نوع موجودیت).
2. entity_type نوع موجودیت جستجو: metro, restaurant, pharmacy, park, hospital, cafe, bank, school, fuel
3. operation یکی از: find_nearby | distance | area | count | info
4. اگر کاربر فقط نام یک مکان را بدون درخواست خاص نوشت -> operation = "info"
5. اگر کاربر نوع موجودیت نزدیک یک مکان خواست -> operation = "find_nearby"

نمونه‌ها:
- "میدان انقلاب" -> {"operation": "info", "location_name": "میدان انقلاب"}
- "مترو نزدیک میدان انقلاب" -> {"operation": "find_nearby", "entity_type": "metro", "location_name": "میدان انقلاب", "radius_meters": 1500}
- "مترو نواب" -> {"operation": "find_nearby", "entity_type": "metro", "location_name": "نواب", "radius_meters": 1500}
- "داروخانه‌های تهران" -> {"operation": "find_nearby", "entity_type": "pharmacy", "location_name": "تهران", "radius_meters": 10000}
- "داروخانه‌های نزدیک ونک" -> {"operation": "find_nearby", "entity_type": "pharmacy", "location_name": "میدان ونک", "radius_meters": 1000}
- "فاصله آزادی تا ونک" -> {"operation": "distance", "location_name": "میدان آزادی", "target_location": "میدان ونک"}
- "مساحت پارک ملت" -> {"operation": "area", "entity_type": "park", "location_name": "پارک ملت"}

فقط JSON برگردان، بدون توضیح اضافی.
"""


def create_plan(question: str) -> dict:
    """تحلیل سوال و تبدیل به طرح JSON"""
    if not settings.openai_api_key:
        raise ValueError("کلید API OpenAI تنظیم نشده است.")

    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    content = response.choices[0].message.content
    plan = json.loads(content)
    plan["query_text"] = question
    return plan
