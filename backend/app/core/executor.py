from app.core.llm_planner import create_plan
from app.geo_tools.osm import geocode_place, find_pois_near, distance_between_places, area_of_place
from app.geo_tools.geometry import format_distance_persian, format_area_persian


def execute_plan(question: str, db) -> dict:
    """اجرای طرح استخراج‌شده از سوال کاربر"""
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


def _error(msg: str, plan: dict) -> dict:
    return {
        "success": False,
        "error": msg,
        "message": msg,
        "type": "error",
        "plan": plan,
    }


def execute_find_nearby(plan: dict, db) -> dict:
    location_name = plan.get("location_name")
    entity_type = plan.get("entity_type")
    radius = plan.get("radius_meters", 1500)

    if not location_name:
        return _error("نام مکان مشخص نشده است.", plan)

    center = geocode_place(db, location_name)
    if not center:
        return _error(f"مکان '{location_name}' پیدا نشد.", plan)

    places = find_pois_near(db, entity_type, center["lat"], center["lon"], radius)

    return {
        "success": True,
        "type": "find_nearby",
        "center": center,
        "entity_type": entity_type,
        "places": places,
        "count": len(places),
        "message": f"{len(places)} مورد در نزدیکی {location_name} یافت شد.",
        "plan": plan,
    }


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
        "message": f"{len(places)} {entity_type} در {location_name} یافت شد.",
        "plan": plan,
    }


def execute_info(plan: dict, db) -> dict:
    """نمایش اطلاعات یک مکان مشخص (مثل میدان انقلاب)"""
    location_name = plan.get("location_name")

    if not location_name:
        return _error("نام مکان مشخص نشده است.", plan)

    place = geocode_place(db, location_name)
    if not place:
        return _error(f"مکان '{location_name}' پیدا نشد.", plan)

    return {
        "success": True,
        "type": "info",
        "center": place,
        "places": [place],
        "count": 1,
        "message": f"اطلاعات مکان '{place['name']}' یافت شد.",
        "plan": plan,
    }
