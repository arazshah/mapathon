import json
import os
from openai import OpenAI

from app.config import settings

client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """
تو یک برنامه‌ریز GIS هوشمند برای شهر تهران هستی.
سوال کاربر را تحلیل کن و فقط یک JSON معتبر برگردان.

قوانین مهم:
1. location_name فقط باید نام مکان خالص باشد (بدون نوع موجودیت).
2. entity_type نوع موجودیت مورد جستجو را مشخص می‌کند (metro, restaurant, pharmacy, park, hospital, ...).
3. operation یکی از: find_nearby | distance | area | count | info
4. اگر سوال فاصله بود: location_name و target_location را پر کن.
5. location_name باید دقیقاً نامی باشد که بتوان در نقشه جستجو کرد.

نمونه‌های خروجی:
- "مترو نزدیک میدان انقلاب" -> {"operation": "find_nearby", "entity_type": "metro", "location_name": "میدان انقلاب", "radius_meters": 1500}
- "رستوران‌های تهران" -> {"operation": "find_nearby", "entity_type": "restaurant", "location_name": "تهران", "radius_meters": 10000}
- "فاصله داروخانه هلال احمر تا میدان آزادی" -> {"operation": "distance", "entity_type": "pharmacy", "location_name": "داروخانه هلال احمر", "target_location": "میدان آزادی"}
- "مساحت پارک ملت" -> {"operation": "area", "entity_type": "park", "location_name": "پارک ملت"}
- "داروخانه‌های نزدیک ونک" -> {"operation": "find_nearby", "entity_type": "pharmacy", "location_name": "میدان ونک", "radius_meters": 1000}

خروجی فقط JSON باشد. هیچ توضیح اضافی نده.
"""


def create_plan(question: str) -> dict:
    """
    تحلیل سوال زبان طبیعی و تبدیل آن به طرح JSON
    """
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
