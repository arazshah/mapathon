"""
LLM Planner - تبدیل سوال زبان طبیعی به برنامه اجرایی
"""
import json
from openai import OpenAI
from app.config import settings

# تعریف ابزارهای موجود برای LLM
TOOLS_SCHEMA = """
ابزارهای موجود:

1. calculate_distance(lat1, lng1, lat2, lng2)
   → محاسبه فاصله بین دو نقطه

2. geocode(address)
   → تبدیل آدرس/نام مکان به مختصات
   ⚠️ برای نام‌های معروف مثل "داروخانه هلال احمر"، "میدان آزادی" استفاده کن!

3. reverse_geocode(lat, lng, radius_meters=100)
   → تبدیل مختصات به نام مکان

4. osm_search(bbox, osm_tags, geometry_type="point", limit=50)
   → جستجوی مکان‌ها در محدوده مشخص (مثل "تمام رستوران‌ها")
   → osm_tags مثال: {"amenity": "restaurant"} یا {"shop": "supermarket"}
   ⚠️ فقط برای جستجوی دسته‌ای (چند نتیجه) استفاده کن، نه برای نام‌های خاص!

5. calculate_area(geometry_geojson)
   → محاسبه مساحت یک polygon

6. create_buffer(geometry_geojson, distance_meters)
   → ایجاد منطقه بافر اطراف یک مکان

7. point_in_polygon(lat, lng, polygon_geojson)
   → بررسی اینکه آیا نقطه داخل منطقه است

8. find_intersection(geom_a, geom_b)
   → پیدا کردن اشتراک دو هندسه

شهرهای موجود در دیتابیس: تهران، ارومیه، اصفهان

bbox های آماده:
- تهران: [51.10, 35.55, 51.65, 35.85]
- اصفهان: [51.50, 32.50, 51.85, 32.80]
- ارومیه: [44.95, 37.45, 45.25, 37.65]

⚠️ ساختار خروجی ابزارها (برای ارجاع با $):

geocode → {"best_match": {"lat": عدد, "lng": عدد, "name": str}, "results": [...], "count": int}
   ارجاع صحیح: $var.best_match.lat و $var.best_match.lng
   ⚠️ هرگز $var.lat ننویس! حتماً best_match را بنویس

calculate_distance → {"distance_km": عدد, "distance_m": عدد, "distance_display": str}
   ارجاع: $var.distance_km یا در template: {var.distance_display}

osm_search → {"features": [...], "count": int}
   در template: {var.count} برای تعداد

reverse_geocode → {"name": str, "type": str, "distance_meters": عدد}

⚠️ برای سوال "کجاست" فقط geocode کافیست، نیازی به reverse_geocode نیست!
   final_answer_template مثال: "{var.best_match.name} در مختصات {var.best_match.lat}, {var.best_match.lng} واقع شده"

مثال‌های صحیح:
- سوال: "فاصله از میدان آزادی تا میدان ولیعصر"
  → استفاده کن: geocode برای هر دو مکان، سپس calculate_distance
  ⚠️ نه osm_search!

- سوال: "رستوران‌های تهران کجا هستند"
  → استفاده کن: osm_search با {"amenity": "restaurant"}

"""

SYSTEM_PROMPT = f"""تو یک برنامه‌ریز GIS هستی.
سوال کاربر را تحلیل کن و یک برنامه اجرایی JSON بساز.

{TOOLS_SCHEMA}

فرمت خروجی (فقط JSON، بدون توضیح اضافه):
{{
  "steps": [
    {{
      "step": 1,
      "tool": "نام_ابزار",
      "params": {{}},
      "description": "توضیح فارسی این قدم",
      "save_as": "نام_متغیر_برای_ذخیره_نتیجه"
    }}
  ],
  "final_answer_template": "قالب پاسخ نهایی با {{متغیرها}}"
}}

قوانین:
- اگر نام مکان معروف است (مثل "میدان آزادی"، "داروخانه هلال احمر") → از geocode استفاده کن
- اگر دنبال چند نتیجه از یک نوع هستی (مثل "تمام بیمارستان‌ها") → از osm_search استفاده کن
- اگر به مختصات نیاز داری اول geocode کن
- نتیجه هر قدم را با save_as ذخیره کن
- در پارامترها می‌توانی از $نام_متغیر برای ارجاع به نتیجه قدم قبل استفاده کنی
- فقط JSON خروجی بده
"""


def create_plan(question: str) -> dict:
    """
    تبدیل سوال زبان طبیعی به plan اجرایی
    اگر API key نداشت از rule-based fallback استفاده می‌کند
    """
    if settings.openai_api_key:
        return _llm_plan(question)
    else:
        return _rule_based_plan(question)


def _llm_plan(question: str) -> dict:
    """استفاده از GPT برای ساخت plan"""
    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        return {"error": str(e), "fallback": True, **_rule_based_plan(question)}


def _rule_based_plan(question: str) -> dict:
    """
    Rule-based fallback بدون نیاز به LLM
    برای سوالات رایج
    """
    q = question.lower()

    # فاصله بین دو مکان
    if any(w in q for w in ["فاصله", "distance", "چقدر دور", "چند کیلومتر"]):
        loc1, loc2 = _extract_two_locations(question)
        return {
            "steps": [
                {
                    "step": 1,
                    "tool": "geocode",
                    "params": {"address": loc1},
                    "description": f"پیدا کردن مختصات '{loc1}'",
                    "save_as": "location1",
                },
                {
                    "step": 2,
                    "tool": "geocode",
                    "params": {"address": loc2},
                    "description": f"پیدا کردن مختصات '{loc2}'",
                    "save_as": "location2",
                },
                {
                    "step": 3,
                    "tool": "calculate_distance",
                    "params": {
                        "lat1": "$location1.best_match.lat",
                        "lng1": "$location1.best_match.lng",
                        "lat2": "$location2.best_match.lat",
                        "lng2": "$location2.best_match.lng",
                    },
                    "description": "محاسبه فاصله",
                    "save_as": "distance_result",
                },
            ],
            "final_answer_template": "فاصله از {location1.best_match.name} تا {location2.best_match.name} برابر با {distance_result.distance_display} است.",
            "rule_based": True,
        }

    # جستجوی رستوران
    if any(w in q for w in ["رستوران", "restaurant", "غذا"]):
        city_bbox = _detect_city_bbox(q)
        return {
            "steps": [
                {
                    "step": 1,
                    "tool": "osm_search",
                    "params": {
                        "bbox": city_bbox,
                        "osm_tags": {"amenity": "restaurant"},
                        "geometry_type": "point",
                        "limit": 20,
                    },
                    "description": "جستجوی رستوران‌ها",
                    "save_as": "restaurants",
                }
            ],
            "final_answer_template": "{restaurants.count} رستوران پیدا شد",
            "rule_based": True,
        }

    # جستجوی بیمارستان
    if any(w in q for w in ["بیمارستان", "hospital", "درمانگاه"]):
        city_bbox = _detect_city_bbox(q)
        return {
            "steps": [
                {
                    "step": 1,
                    "tool": "osm_search",
                    "params": {
                        "bbox": city_bbox,
                        "osm_tags": {"amenity": "hospital"},
                        "geometry_type": "point",
                        "limit": 20,
                    },
                    "description": "جستجوی بیمارستان‌ها",
                    "save_as": "hospitals",
                }
            ],
            "final_answer_template": "{hospitals.count} بیمارستان پیدا شد",
            "rule_based": True,
        }

    # geocode ساده
    if any(w in q for w in ["کجاست", "کجا", "مختصات", "آدرس", "where is"]):
        return {
            "steps": [
                {
                    "step": 1,
                    "tool": "geocode",
                    "params": {"address": _clean_query(question)},
                    "description": "جستجوی مکان",
                    "save_as": "location",
                }
            ],
            "final_answer_template": "مکان در مختصات {location.best_match.lat}, {location.best_match.lng} پیدا شد",
            "rule_based": True,
        }

    # پیش‌فرض: geocode
    return {
        "steps": [
            {
                "step": 1,
                "tool": "geocode",
                "params": {"address": _clean_query(question)},
                "description": "جستجوی مکان",
                "save_as": "location",
            }
        ],
        "final_answer_template": "نتیجه: {location}",
        "rule_based": True,
    }


def _clean_query(text: str) -> str:
    """حذف کلمات سوالی و اضافه از متن برای geocode بهتر"""
    stopwords = [
        "کجاست", "کجا", "کجاس", "مختصات", "آدرس", "where", "is",
        "را", "رو", "میدان", "چیست", "کن", "پیدا", "نشانم", "بده",
        "نشان", "بگو", "؟", "?",
    ]
    cleaned = text
    for w in stopwords:
        cleaned = cleaned.replace(w, " ")
    cleaned = " ".join(cleaned.split()).strip()
    return cleaned if cleaned else text


def _detect_city_bbox(text: str) -> list:
    """تشخیص شهر از متن"""
    if any(w in text for w in ["اصفهان", "isfahan"]):
        return [51.50, 32.50, 51.85, 32.80]
    if any(w in text for w in ["ارومیه", "urmia"]):
        return [44.95, 37.45, 45.25, 37.65]
    return [51.10, 35.55, 51.65, 35.85]  # تهران پیش‌فرض


def _extract_two_locations(text: str) -> tuple:
    """
    استخراج دو مکان از متن
    مثال: "فاصله از داروخانه هلال احمر تا میدان آزادی"
    → ("داروخانه هلال احمر", "میدان آزادی")
    """
    text_clean = text.lower()
    
    # جدا کردن به دو بخش توسط "تا"
    separators = ["تا ", " تا "]
    loc1 = None
    loc2 = None
    
    for sep in separators:
        if sep in text_clean:
            parts = text.split(sep, 1)  # فقط اول رو جدا کن
            if len(parts) == 2:
                loc1 = parts[0]
                loc2 = parts[1]
                break
    
    if not loc1 or not loc2:
        # اگر "تا" نبود، از "و" استفاده کن
        if " و " in text_clean:
            parts = text.split(" و ", 1)
            loc1 = parts[0]
            loc2 = parts[1]
    
    # پاک کردن کلمات اضافی
    remove_words = [
        "فاصله", "distance", "از", "from",
        "بین", "between", "چقدر", "دور", "است", "is",
        "کیلومتر", "km", "متر", "m", "؟", "?",
    ]
    
    for word in remove_words:
        loc1 = loc1.replace(word, " ").strip()
        loc2 = loc2.replace(word, " ").strip()
    
    # حذف فاصلهای اضافی
    loc1 = " ".join(loc1.split()).strip()
    loc2 = " ".join(loc2.split()).strip()
    
    # fallback
    if not loc1:
        loc1 = "تهران"
    if not loc2:
        loc2 = "اصفهان"
    
    return loc1, loc2
