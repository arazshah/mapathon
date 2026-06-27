"""
LLM Planner - تبدیل سوال زبان طبیعی به برنامه اجرایی
"""
import json
from openai import OpenAI
from app.config import settings

TOOLS_SCHEMA = """
ابزارهای موجود:

1. calculate_distance(lat1, lng1, lat2, lng2)
   → محاسبه فاصله بین دو نقطه
   خروجی: {"distance_km": عدد, "distance_m": عدد, "distance_display": str}

2. geocode(address)
   → تبدیل آدرس/نام مکان به مختصات
   خروجی: {"best_match": {"lat": عدد, "lng": عدد, "name": str}, "results": [...], "count": int}
   ⚠️ ارجاع صحیح: {var.best_match.lat} و {var.best_match.lng} و {var.best_match.name}
   ⚠️ هرگز {var.lat} ننویس!

3. reverse_geocode(lat, lng, radius_meters=100)
   → تبدیل مختصات به نام مکان
   خروجی: {"name": str, "type": str, "distance_meters": عدد}

4. osm_search(bbox, osm_tags, geometry_type="point", limit=50)
   → جستجوی دسته‌ای مکان‌ها در محدوده مشخص
   → osm_tags مثال: {"amenity": "restaurant"} یا {"shop": "supermarket"}
   خروجی: {"features": [...], "count": int}
   ⚠️ فقط برای جستجوی چند نتیجه، نه نام‌های خاص!
   ارجاع: {var.count} برای تعداد

5. calculate_area(geometry_geojson)
   → محاسبه مساحت یک polygon
   خروجی: {"success": true, "area_m2": عدد, "area_hectares": عدد, "area_km2": عدد}
   ارجاع صحیح: {var.area_m2} یا {var.area_hectares} یا {var.area_km2}
   ⚠️ هرگز {var} به تنهایی ننویس! حتماً فیلد مشخص بنویس.

6. create_buffer(geometry_geojson, distance_meters)
   → ایجاد منطقه بافر اطراف یک مکان
   خروجی: {"geometry": {...}, "buffer_meters": عدد}

7. point_in_polygon(lat, lng, polygon_geojson)
   → بررسی اینکه آیا نقطه داخل منطقه است
   خروجی: {"inside": true/false, "point": [...], "polygon_area_m2": عدد}
   ارجاع: {var.inside}

8. find_intersection(geom_a_geojson, geom_b_geojson)
   → پیدا کردن اشتراک دو هندسه
   ⚠️ پارامترها دقیقاً: geom_a_geojson و geom_b_geojson
   خروجی: {"success": true, "geometry": {...}, "area_m2": عدد}

شهرهای موجود: تهران، ارومیه، اصفهان

bbox های آماده:
- تهران: [51.10, 35.55, 51.65, 35.85]
- اصفهان: [51.50, 32.50, 51.85, 32.80]
- ارومیه: [44.95, 37.45, 45.25, 37.65]

⚠️ تگ‌های صحیح OSM (فقط از این ستون‌ها استفاده کن):
- مترو/ایستگاه قطار → {"railway": "station"}   (هرگز {"station": ...} ننویس!)
- داروخانه → {"amenity": "pharmacy"}
- بیمارستان → {"amenity": "hospital"}
- رستوران → {"amenity": "restaurant"}
- مدرسه → {"amenity": "school"}
- پارک → {"leisure": "park"}
- فروشگاه → {"shop": "supermarket"}

⚠️ برای محاسبه مساحت یک مکان نام‌دار (مثل پارک ملت):
   قدم۱: geocode با geometry_type تشخیص خودکار → خروجی best_match.geojson دارد
   قدم۲: calculate_area با geometry_geojson = $loc.best_match.geojson
   ⚠️ مقدار geometry_geojson باید مستقیماً $var.best_match.geojson باشد (نه string، نه دستی)

⚠️ آدرس‌ها را بدون پسوند ", تهران" بفرست. فقط نام خود مکان (مثلاً "میدان ونک" نه "میدان ونک، تهران")
"""

SYSTEM_PROMPT = f"""تو یک برنامه‌ریز GIS هستی.
سوال کاربر را تحلیل کن و یک برنامه اجرایی JSON بساز.

{TOOLS_SCHEMA}

فرمت خروجی (فقط JSON، بدون توضیح):
{{
  "steps": [
    {{
      "step": 1,
      "tool": "نام_ابزار",
      "params": {{}},
      "description": "توضیح فارسی",
      "save_as": "نام_متغیر"
    }}
  ],
  "final_answer_template": "پاسخ با {{متغیر.فیلد}}"
}}

قوانین مهم برای final_answer_template:
1. همیشه از {{var.field}} استفاده کن، نه [var.field] و نه {{var}} تنها
2. برای مساحت: {{area_result.area_m2}} متر مربع ({{area_result.area_hectares}} هکتار)
3. برای فاصله: {{distance_result.distance_display}}
4. برای geocode: {{location.best_match.name}} در مختصات {{location.best_match.lat}}, {{location.best_match.lng}}
5. برای osm_search: {{results.count}} مورد یافت شد
6. برای point_in_polygon: اگر {{check.inside}} برابر true باشد → داخل منطقه است
7. برای نزدیک‌ترین مکان از osm_search: {{results.features[0].properties.name}}
   ⚠️ این فرمت کار نمی‌کند! به جایش بنویس: نزدیک‌ترین مورد در نتایج نمایش داده می‌شود

مثال‌های صحیح:
- فاصله → "فاصله از {{loc1.best_match.name}} تا {{loc2.best_match.name}} برابر {{dist.distance_display}} است"
- مساحت → "مساحت {{area.area_m2}} متر مربع ({{area.area_hectares}} هکتار) است"
- جستجو → "{{results.count}} مورد یافت شد"
- موقعیت → "{{loc.best_match.name}} در {{loc.best_match.lat}}, {{loc.best_match.lng}} قرار دارد"

فقط JSON خروجی بده.
"""


def create_plan(question: str) -> dict:
    """تبدیل سوال زبان طبیعی به plan اجرایی"""
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
    """Rule-based fallback بدون نیاز به LLM"""
    q = question.lower()

    if any(w in q for w in ["فاصله", "distance", "چقدر دور", "چند کیلومتر"]):
        loc1, loc2 = _extract_two_locations(question)
        return {
            "steps": [
                {"step": 1, "tool": "geocode", "params": {"address": loc1},
                 "description": f"مختصات '{loc1}'", "save_as": "location1"},
                {"step": 2, "tool": "geocode", "params": {"address": loc2},
                 "description": f"مختصات '{loc2}'", "save_as": "location2"},
                {"step": 3, "tool": "calculate_distance",
                 "params": {
                     "lat1": "$location1.best_match.lat",
                     "lng1": "$location1.best_match.lng",
                     "lat2": "$location2.best_match.lat",
                     "lng2": "$location2.best_match.lng",
                 },
                 "description": "محاسبه فاصله", "save_as": "distance_result"},
            ],
            "final_answer_template": "فاصله از {location1.best_match.name} تا {location2.best_match.name} برابر {distance_result.distance_display} است.",
            "rule_based": True,
        }

    if any(w in q for w in ["رستوران", "restaurant"]):
        return {
            "steps": [{"step": 1, "tool": "osm_search",
                       "params": {"bbox": _detect_city_bbox(q), "osm_tags": {"amenity": "restaurant"}, "limit": 20},
                       "description": "جستجوی رستوران‌ها", "save_as": "restaurants"}],
            "final_answer_template": "{restaurants.count} رستوران یافت شد",
            "rule_based": True,
        }

    if any(w in q for w in ["بیمارستان", "hospital"]):
        return {
            "steps": [{"step": 1, "tool": "osm_search",
                       "params": {"bbox": _detect_city_bbox(q), "osm_tags": {"amenity": "hospital"}, "limit": 20},
                       "description": "جستجوی بیمارستان‌ها", "save_as": "hospitals"}],
            "final_answer_template": "{hospitals.count} بیمارستان یافت شد",
            "rule_based": True,
        }

    return {
        "steps": [{"step": 1, "tool": "geocode",
                   "params": {"address": _clean_query(question)},
                   "description": "جستجوی مکان", "save_as": "location"}],
        "final_answer_template": "{location.best_match.name} در {location.best_match.lat}, {location.best_match.lng} قرار دارد",
        "rule_based": True,
    }


def _clean_query(text: str) -> str:
    stopwords = ["کجاست", "کجا", "مختصات", "آدرس", "where", "is",
                 "را", "رو", "چیست", "کن", "پیدا", "نشانم", "بده", "نشان", "بگو", "؟", "?"]
    cleaned = text
    for w in stopwords:
        cleaned = cleaned.replace(w, " ")
    return " ".join(cleaned.split()).strip() or text


def _detect_city_bbox(text: str) -> list:
    if any(w in text for w in ["اصفهان", "isfahan"]):
        return [51.50, 32.50, 51.85, 32.80]
    if any(w in text for w in ["ارومیه", "urmia"]):
        return [44.95, 37.45, 45.25, 37.65]
    return [51.10, 35.55, 51.65, 35.85]


def _extract_two_locations(text: str) -> tuple:
    text_clean = text.lower()
    for sep in ["تا ", " تا "]:
        if sep in text_clean:
            parts = text.split(sep, 1)
            if len(parts) == 2:
                loc1, loc2 = parts[0], parts[1]
                break
    else:
        if " و " in text_clean:
            parts = text.split(" و ", 1)
            loc1, loc2 = parts[0], parts[1]
        else:
            return "تهران", "اصفهان"

    remove_words = ["فاصله", "distance", "از", "from", "بین", "between",
                    "چقدر", "دور", "است", "کیلومتر", "متر", "؟", "?"]
    for word in remove_words:
        loc1 = loc1.replace(word, " ").strip()
        loc2 = loc2.replace(word, " ").strip()

    loc1 = " ".join(loc1.split()).strip() or "تهران"
    loc2 = " ".join(loc2.split()).strip() or "اصفهان"
    return loc1, loc2
