import os
import re
import json
import requests
from sqlalchemy import text
from typing import List, Dict, Any

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

TEHRAN_BBOX = "51.0,35.5,51.8,35.9"

def call_openai(messages: list) -> str:
    if not OPENAI_API_KEY:
        return ""
    try:
        res = requests.post(
            f"{OPENAI_BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={"model": OPENAI_MODEL, "messages": messages, "temperature": 0.1},
            timeout=30
        )
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"خطا در OpenAI: {e}"

def detect_intent(question: str) -> Dict[str, Any]:
    q = question.strip()
    lowered = q.lower()

    # مترو
    if re.search(r"مترو|ایستگاه مترو|متروی", q):
        return {"type": "metro", "location": "تهران"}

    # رستوران
    if re.search(r"رستوران|غذا|کافه", q):
        return {"type": "restaurant", "location": "تهران"}

    # داروخانه
    if re.search(r"داروخانه|درمانگاه|کلینیک", q):
        return {"type": "pharmacy", "location": "تهران"}

    # فاصله
    distance_match = re.search(r"فاصله\s+(.+?)\s+تا\s+(.+)", q)
    if distance_match or re.search(r"فاصله", q):
        return {"type": "distance", "location": "تهران", "raw": q}

    # مساحت
    if re.search(r"مساحت|متراژ|اندازه", q):
        return {"type": "area", "location": "تهران", "raw": q}

    # نزدیک‌ترین
    if re.search(r"نزدیک|نزدیکترین|مجاور|کنار", q):
        return {"type": "nearest", "location": "تهران", "raw": q}

    # fallback
    return {"type": "unknown", "location": "تهران", "raw": q}

def find_places(db, place_type: str, city: str = "تهران", limit: int = 50) -> List[Dict]:
    # تطابق ساده type با tagهای OSM
    type_map = {
        "metro": ("planet_osm_point", "railway = 'station' AND (tags->'station' = 'subway' OR tags->'name' LIKE '%مترو%' OR tags->'name:en' ILIKE '%metro%')"),
        "restaurant": ("planet_osm_point", "amenity = 'restaurant'"),
        "pharmacy": ("planet_osm_point", "amenity = 'pharmacy'"),
        "hospital": ("planet_osm_point", "amenity = 'hospital'"),
        "school": ("planet_osm_point", "amenity = 'school'"),
    }

    table, where = type_map.get(place_type, (None, None))
    if not table:
        return []

    sql = f"""
    SELECT osm_id, name, tags, ST_AsGeoJSON(ST_Transform(way, 4326)) AS geom
    FROM {table}
    WHERE {where}
      AND ST_Within(way, (SELECT way FROM planet_osm_polygon WHERE name ILIKE 'Tehran' OR name ILIKE 'تهران' LIMIT 1))
    LIMIT {limit}
    """
    try:
        rows = db.execute(text(sql)).mappings().all()
        return [dict(r) for r in rows]
    except Exception as e:
        return []

def geocode_name(db, name: str) -> Dict:
    sql = """
    SELECT osm_id, name, tags, ST_AsGeoJSON(ST_Transform(way, 4326)) AS geom,
           ST_X(ST_Transform(way, 4326)) AS lon,
           ST_Y(ST_Transform(way, 4326)) AS lat
    FROM planet_osm_point
    WHERE name ILIKE :name
    ORDER BY ST_Area(way) DESC NULLS LAST
    LIMIT 1
    """
    try:
        row = db.execute(text(sql), {"name": f"%{name}%"}).mappings().first()
        if row:
            return dict(row)
    except Exception:
        pass

    # امتحان در polygon
    sql2 = """
    SELECT osm_id, name, tags, ST_AsGeoJSON(ST_Transform(way, 4326)) AS geom,
           ST_X(ST_Centroid(ST_Transform(way, 4326))) AS lon,
           ST_Y(ST_Centroid(ST_Transform(way, 4326))) AS lat
    FROM planet_osm_polygon
    WHERE name ILIKE :name
    LIMIT 1
    """
    try:
        row = db.execute(text(sql2), {"name": f"%{name}%"}).mappings().first()
        if row:
            return dict(row)
    except Exception:
        pass
    return None

def process_question(db, question: str) -> Dict[str, Any]:
    intent = detect_intent(question)

    if intent["type"] in ["metro", "restaurant", "pharmacy"]:
        places = find_places(db, intent["type"])
        count = len(places)
        type_label = {
            "metro": "ایستگاه مترو",
            "restaurant": "رستوران",
            "pharmacy": "داروخانه"
        }.get(intent["type"], "مکان")

        features = []
        for p in places:
            geom = json.loads(p["geom"]) if isinstance(p["geom"], str) else p["geom"]
            features.append({
                "type": "Feature",
                "geometry": geom,
                "properties": {
                    "id": p["osm_id"],
                    "name": p["name"] or "بدون نام",
                    "type": type_label
                }
            })

        # محاسبه مرکز
        center = [51.3890, 35.6892]
        if features:
            lons = [f["geometry"]["coordinates"][0] for f in features]
            lats = [f["geometry"]["coordinates"][1] for f in features]
            center = [sum(lons)/len(lons), sum(lats)/len(lats)]

        return {
            "answer": f"{count} {type_label} در تهران یافت شد.",
            "map": {
                "type": "FeatureCollection",
                "features": features,
                "center": center,
                "zoom": 12
            },
            "report": {
                "type": "list",
                "count": count,
                "items": [
                    {"name": f["properties"]["name"], "id": f["properties"]["id"]}
                    for f in features[:20]
                ]
            }
        }

    elif intent["type"] == "distance":
        # استخراج نام‌ها با OpenAI
        prompt = f"""
        از این جمله فارسی دو نقطه مبدأ و مقصد را استخراج کن. فقط JSON با کلیدهای source و destination برگردان:
        "{question}"
        """
        raw = call_openai([{"role": "user", "content": prompt}])
        try:
            match = re.search(r'\\{.*?\\}', raw, re.DOTALL)
            points = json.loads(match.group(0)) if match else {}
            src = geocode_name(db, points.get("source", ""))
            dst = geocode_name(db, points.get("destination", ""))
            if src and dst:
                sql = """
                SELECT ST_Distance(
                    ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:src), 4326), 3857),
                    ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:dst), 4326), 3857)
                ) / 1000 AS dist_km
                """
                row = db.execute(text(sql), {"src": src["geom"], "dst": dst["geom"]}).mappings().first()
                dist = round(row["dist_km"], 2) if row else 0
                return {
                    "answer": f"فاصله تقریبی از {src['name']} تا {dst['name']} حدود {dist} کیلومتر است.",
                    "map": {
                        "type": "FeatureCollection",
                        "features": [
                            {"type": "Feature", "geometry": json.loads(src["geom"]) if isinstance(src["geom"], str) else src["geom"], "properties": {"name": src["name"]}},
                            {"type": "Feature", "geometry": json.loads(dst["geom"]) if isinstance(dst["geom"], str) else dst["geom"], "properties": {"name": dst["name"]}}
                        ],
                        "center": [(src["lon"] + dst["lon"])/2, (src["lat"] + dst["lat"])/2],
                        "zoom": 13
                    },
                    "report": {"type": "text", "content": f"فاصله: {dist} km"}
                }
        except Exception as e:
            return {"answer": f"خطا در محاسبه فاصله: {e}", "map": {"type": "FeatureCollection", "features": []}, "report": {"type": "error", "content": str(e)}}

    elif intent["type"] == "area":
        # پیدا کردن نام مکان
        prompt = f"نام مکان را از این جمله فارسی استخراج کن. فقط یک کلمه یا عبارت کوتاه: '{question}'"
        name = call_openai([{"role": "user", "content": prompt}]).strip().strip('"').strip("'")
        place = geocode_name(db, name)
        if place:
            sql = "SELECT ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326), 3857)) AS area FROM (SELECT 1) t"
            row = db.execute(text(sql), {"geom": place["geom"]}).mappings().first()
            area = round(row["area"], 2) if row else 0
            return {
                "answer": f"مساحت تقریبی {place['name']} حدود {area} متر مربع است.",
                "map": {
                    "type": "FeatureCollection",
                    "features": [{"type": "Feature", "geometry": json.loads(place["geom"]) if isinstance(place["geom"], str) else place["geom"], "properties": {"name": place["name"]}}],
                    "center": [place["lon"], place["lat"]],
                    "zoom": 15
                },
                "report": {"type": "text", "content": f"مساحت: {area} متر مربع"}
            }

    elif intent["type"] == "nearest":
        # نزدیک‌ترین
        prompt = f"""
        از این جمله فارسی دو نقطه را استخراج کن: target (مکان هدف) و reference (مکان مرجع). فقط JSON با کلیدهای target و reference:
        "{question}"
        """
        raw = call_openai([{"role": "user", "content": prompt}])
        try:
            match = re.search(r'\\{.*?\\}', raw, re.DOTALL)
            points = json.loads(match.group(0)) if match else {}
            ref = geocode_name(db, points.get("reference", ""))
            target_type = "pharmacy" if "داروخانه" in question else "metro" if "مترو" in question else "restaurant"
            if ref:
                sql = f"""
                SELECT osm_id, name, tags, ST_AsGeoJSON(ST_Transform(way, 4326)) AS geom,
                       ST_Distance(way, ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(:ref), 4326), 3857)) AS dist
                FROM planet_osm_point
                WHERE amenity = :type OR railway = 'station'
                ORDER BY dist
                LIMIT 5
                """
                rows = db.execute(text(sql), {"ref": ref["geom"], "type": target_type}).mappings().all()
                features = []
                for r in rows:
                    features.append({
                        "type": "Feature",
                        "geometry": json.loads(r["geom"]) if isinstance(r["geom"], str) else r["geom"],
                        "properties": {"name": r["name"] or "بدون نام", "distance_m": round(r["dist"], 1)}
                    })
                return {
                    "answer": f"۵ {target_type} نزدیک به {ref['name']} یافت شد.",
                    "map": {
                        "type": "FeatureCollection",
                        "features": features,
                        "center": [ref["lon"], ref["lat"]],
                        "zoom": 15
                    },
                    "report": {"type": "list", "count": len(features), "items": [{"name": f["properties"]["name"], "distance": f["properties"]["distance_m"]} for f in features]}
                }
        except Exception as e:
            return {"answer": f"خطا در یافتن نزدیک‌ترین: {e}", "map": {"type": "FeatureCollection", "features": []}, "report": {"type": "error", "content": str(e)}}

    # fallback
    return {
        "answer": "متأسفانه نتوانستم این سوال را پردازش کنم. لطفاً واضح‌تر بپرسید.",
        "map": {"type": "FeatureCollection", "features": []},
        "report": {"type": "text", "content": "پردازش انجام نشد"}
    }
