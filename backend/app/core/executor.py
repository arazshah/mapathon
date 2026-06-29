from sqlalchemy import text
from app.core.llm_planner import create_plan
from app.geo_tools.osm import (
    geocode_place, find_pois_near, find_entity_by_name,
    distance_between_places, area_of_place,
)
    find_entity_by_name,
    geocode_place, find_pois_near, distance_between_places, area_of_place,
    ENTITY_TAG_CONDITIONS,
)
from app.geo_tools.geometry import format_distance_persian, format_area_persian


def execute_plan(question: str, db) -> dict:
    plan = create_plan(question)
    operation = plan.get("operation")

    if operation == "find_nearby":
        return execute_find_nearby(plan, db)
    elif operation == "distance":
        return execute_distance(plan, db)
    elif operation == "area":
        return execute_area(plan, db)
    elif operation == "count":
        return execute_count(plan, db)
    elif operation == "info":
        return execute_info(plan, db)
    else:
        return _error(f"عملیات '{operation}' پشتیبانی نمی‌شود.", plan)


def _error(message: str, plan: dict) -> dict:
    return {
        "success": False, "error": message, "plan": plan,
        "message": message, "type": "error",
    }


def _find_entity_by_name(db, entity_type: str, name: str) -> list:
    """
    جستجوی مستقیم یک نوع موجودیت بر اساس نام آن.
    مثلاً 'مترو نواب' -> ایستگاه مترویی که نامش شامل نواب است.
    """
    tag_condition = ENTITY_TAG_CONDITIONS.get(entity_type)
    if not tag_condition or ":pattern" in tag_condition:
        return []

    sql = text(f"""
        SELECT 
            osm_id, name, tags,
            ST_Y(ST_Transform(way, 4326)) as lat,
            ST_X(ST_Transform(way, 4326)) as lon
        FROM planet_osm_point
        WHERE {tag_condition}
          AND name ILIKE :name
        LIMIT 20
    """)
    rows = db.execute(sql, {"name": f"%{name}%"}).mappings().all()

    results = []
    for row in rows:
        if row["lat"] is None:
            continue
        results.append({
            "osm_id": row["osm_id"],
            "name": row["name"] or "بدون نام",
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "distance_meters": 0,
            "tags": dict(row["tags"]) if row["tags"] else {},
        })
    return results


def execute_find_nearby(plan: dict, db) -> dict:
    location_name = plan.get("location_name")
    entity_type = plan.get("entity_type")
    radius = plan.get("radius_meters", 1500)

    if not location_name:
        return _error("نام مکان مشخص نشده است.", plan)

    # استراتژی ۱: جستجوی مستقیم موجودیت با همان نام
    # مثلاً 'مترو نواب' -> ایستگاهی که نامش نواب است
    direct = _find_entity_by_name(db, entity_type, location_name)
    if direct:
        return {
            "success": True,
            "type": "find_nearby",
            "center": direct[0],
            "entity_type": entity_type,
            "places": direct,
            "count": len(direct),
            "message": f"{len(direct)} {_label(entity_type)} با نام «{location_name}» یافت شد.",
            "plan": plan,
        }

    # استراتژی ۲: geocode مکان، سپس جستجوی نزدیکی
    center = geocode_place(db, location_name)
    if not center:
        return _error(f"مکان '{location_name}' پیدا نشد.", plan)

    places = find_pois_near(db, entity_type, center["lat"], center["lon"], radius)

    if not places:
        return {
            "success": True,
            "type": "find_nearby",
            "center": center,
            "entity_type": entity_type,
            "places": [],
            "count": 0,
            "message": f"در شعاع {radius} متری «{location_name}» هیچ {_label(entity_type)} یافت نشد.",
            "plan": plan,
        }

    return {
        "success": True,
        "type": "find_nearby",
        "center": center,
        "entity_type": entity_type,
        "places": places,
        "count": len(places),
        "message": f"{len(places)} {_label(entity_type)} در نزدیکی «{location_name}» یافت شد.",
        "plan": plan,
    }


def _label(entity_type: str) -> str:
    labels = {
        "metro": "ایستگاه مترو", "subway": "ایستگاه مترو",
        "restaurant": "رستوران", "pharmacy": "داروخانه",
        "hospital": "بیمارستان", "park": "پارک",
        "school": "مدرسه", "cafe": "کافه", "bank": "بانک",
        "fuel": "پمپ بنزین", "atm": "خودپرداز", "bus_stop": "ایستگاه اتوبوس",
    }
    return labels.get(entity_type, entity_type or "مورد")


def execute_distance(plan: dict, db) -> dict:
    from_name = plan.get("location_name")
    to_name = plan.get("target_location")

    if not from_name or not to_name:
        return _error("دو مکان برای محاسبه فاصله نیاز است.", plan)

    result = distance_between_places(db, from_name, to_name)
    if not result:
        return _error(f"یکی از مکان‌ها پیدا نشد: '{from_name}' یا '{to_name}'", plan)

    return {
        "success": True,
        "type": "distance",
        "from": result["from"],
        "to": result["to"],
        "center": result["from"],
        "places": [result["from"], result["to"]],
        "distance_meters": result["distance_meters"],
        "message": format_distance_persian(result["distance_meters"]),
        "plan": plan,
    }


def execute_area(plan: dict, db) -> dict:
    location_name = plan.get("location_name")
    entity_type = plan.get("entity_type")

    result = area_of_place(db, location_name, entity_type)
    if not result:
        return _error(f"مکان '{location_name}' برای محاسبه مساحت پیدا نشد.", plan)

    return {
        "success": True,
        "type": "area",
        "place": result["place"],
        "center": result["place"],
        "places": [result["place"]],
        "area_m2": result["area_m2"],
        "message": format_area_persian(result["area_m2"]),
        "plan": plan,
    }


def execute_count(plan: dict, db) -> dict:
    location_name = plan.get("location_name")
    entity_type = plan.get("entity_type")
    radius = plan.get("radius_meters", 10000)

    center = geocode_place(db, location_name)
    if not center:
        return _error(f"مکان '{location_name}' پیدا نشد.", plan)

    places = find_pois_near(db, entity_type, center["lat"], center["lon"], radius)

    return {
        "success": True,
        "type": "count",
        "count": len(places),
        "center": center,
        "places": places,
        "message": f"{len(places)} {_label(entity_type)} در «{location_name}» یافت شد.",
        "plan": plan,
    }


def execute_info(plan: dict, db) -> dict:
    location_name = plan.get("location_name")
    if not location_name:
        return _error("نام مکان مشخص نشده است.", plan)

    place = geocode_place(db, location_name)
    if not place:
        return _error(f"مکان '{location_name}' پیدا نشد.", plan)

    return {
        "success": True,
        "type": "info",
        "place": place,
        "center": place,
        "places": [place],
        "count": 1,
        "message": f"مکان «{place['name']}» یافت شد.",
        "plan": plan,
    }
