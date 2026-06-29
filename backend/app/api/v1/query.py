from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any

from app.core.database import get_postgis_db
from app.core.executor import execute_plan

router = APIRouter(tags=["query"])


class QueryRequest(BaseModel):
    question: str


def to_geojson(result: dict) -> dict:
    """
    تبدیل places به فرمت GeoJSON که فرانت‌اند انتظار دارد.
    """
    places = result.get("places", []) or []
    features = []

    for place in places:
        if place.get("lat") is None or place.get("lon") is None:
            continue

        properties = {
            "name": place.get("name", "بدون نام"),
            "osm_id": place.get("osm_id"),
        }
        # افزودن distance اگر وجود دارد
        if place.get("distance_meters"):
            properties["distance_meters"] = place["distance_meters"]

        # افزودن amenity/category از tags
        tags = place.get("tags", {}) or {}
        if tags.get("amenity"):
            properties["amenity"] = tags["amenity"]
        if tags.get("station"):
            properties["category"] = "ایستگاه مترو"
        elif tags.get("leisure") == "park":
            properties["category"] = "پارک"

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [place["lon"], place["lat"]],  # GeoJSON: [lng, lat]
            },
            "properties": properties,
        })

    return {
        "geojson": {
            "type": "FeatureCollection",
            "features": features,
        }
    }


@router.post("/query")
def query(request: QueryRequest, db: Session = Depends(get_postgis_db)) -> dict[str, Any]:
    """
    دریافت سوال زبان طبیعی و پاسخ GIS با فرمت سازگار با فرانت‌اند
    """
    try:
        result = execute_plan(request.question, db)

        if not result.get("success"):
            return {
                "success": False,
                "error": result.get("error") or result.get("message", "خطا در پردازش"),
                "message": result.get("message", ""),
            }

        # ساخت پاسخ سازگار با فرانت
        return {
            "success": True,
            "answer": result.get("message", ""),
            "map": to_geojson(result),
            "type": result.get("type"),
            "center": result.get("center"),
            "count": result.get("count", 0),
            "distance_meters": result.get("distance_meters"),
            "area_m2": result.get("area_m2"),
            "debug": {
                "plan": result.get("plan"),
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "خطا در پردازش سوال",
        }