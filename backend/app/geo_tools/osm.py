"""
ابزارهای مرتبط با دیتابیس OSM و PostGIS
"""
from sqlalchemy import text
from app.core.database import engine
import json


def geocode_from_postgis(address: str, limit: int = 5) -> dict:
    """
    جستجوی آدرس در داده‌های OSM با اولویت‌بندی هوشمند
    اولویت: مطابقت دقیق > مکان‌های مهم (place/station) > بقیه
    """
    if not isinstance(address, str):
        raise ValueError(f"address باید string باشه، نه {type(address)}")
    
    try:
        query_point = text("""
            SELECT 
                name, amenity, place, shop, tourism, railway, highway,
                ST_Y(ST_Transform(way, 4326)) as lat,
                ST_X(ST_Transform(way, 4326)) as lng,
                ST_AsGeoJSON(ST_Transform(way, 4326)) as geojson,
                CASE
                    WHEN name = :exact THEN 100
                    WHEN place IS NOT NULL THEN 90
                    WHEN railway = 'station' THEN 85
                    WHEN railway IS NOT NULL THEN 70
                    WHEN highway IS NOT NULL THEN 60
                    WHEN name ILIKE :starts THEN 50
                    ELSE 10
                END as priority
            FROM planet_osm_point
            WHERE name ILIKE :search
            ORDER BY priority DESC, length(name) ASC
            LIMIT :limit
        """)

        query_polygon = text("""
            SELECT 
                name, amenity, place, shop, tourism,
                NULL as railway, NULL as highway,
                ST_Y(ST_Centroid(ST_Transform(way, 4326))) as lat,
                ST_X(ST_Centroid(ST_Transform(way, 4326))) as lng,
                ST_AsGeoJSON(ST_Centroid(ST_Transform(way, 4326))) as geojson,
                CASE
                    WHEN name = :exact THEN 100
                    WHEN place IS NOT NULL THEN 90
                    WHEN name ILIKE :starts THEN 50
                    ELSE 10
                END as priority
            FROM planet_osm_polygon
            WHERE name ILIKE :search
            ORDER BY priority DESC, length(name) ASC
            LIMIT :limit
        """)

        params = {
            "search": f"%{address}%",
            "exact": address,
            "starts": f"{address}%",
            "limit": limit,
        }

        with engine.connect() as conn:
            rows = conn.execute(query_point, params).fetchall()
            if not rows:
                rows = conn.execute(query_polygon, params).fetchall()

        if not rows:
            return {"success": False, "error": f"آدرس '{address}' پیدا نشد"}

        results = []
        for row in rows:
            results.append({
                "name": row.name,
                "lat": round(float(row.lat), 6) if row.lat else None,
                "lng": round(float(row.lng), 6) if row.lng else None,
                "type": (row.amenity or row.shop or row.tourism
                         or row.place or getattr(row, "railway", None)
                         or getattr(row, "highway", None)),
                "geojson": json.loads(row.geojson) if row.geojson else None,
            })

        return {
            "success": True,
            "results": results,
            "count": len(results),
            "best_match": results[0] if results else None,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def osm_spatial_query(
    bbox: list, osm_tags: dict,
    geometry_type: str = "point", limit: int = 100
) -> dict:
    """
    جستجوی مکانی در داده‌های OSM
    bbox: [minx, miny, maxx, maxy]
    """
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        raise ValueError(f"bbox باید list/tuple با 4 عنصر باشه")
    
    try:
        table_map = {
            "point": "planet_osm_point",
            "polygon": "planet_osm_polygon",
            "line": "planet_osm_line",
        }
        table = table_map.get(geometry_type, "planet_osm_point")

        tag_conditions = []
        params = {
            "minx": bbox[0], "miny": bbox[1],
            "maxx": bbox[2], "maxy": bbox[3], "limit": limit,
        }
        for i, (key, value) in enumerate(osm_tags.items()):
            param_name = f"tag_val_{i}"
            tag_conditions.append(f"{key} = :{param_name}")
            params[param_name] = value
        tag_where = " AND ".join(tag_conditions) if tag_conditions else "1=1"

        query = text(f"""
            SELECT osm_id, name, amenity, shop, tourism,
                ST_AsGeoJSON(ST_Transform(way, 4326)) as geojson,
                ST_Y(ST_Transform(CASE WHEN GeometryType(way)='POINT' THEN way ELSE ST_Centroid(way) END, 4326)) as lat,
                ST_X(ST_Transform(CASE WHEN GeometryType(way)='POINT' THEN way ELSE ST_Centroid(way) END, 4326)) as lng
            FROM {table}
            WHERE {tag_where}
                AND ST_Transform(way, 4326) && ST_MakeEnvelope(:minx, :miny, :maxx, :maxy, 4326)
            LIMIT :limit
        """)

        with engine.connect() as conn:
            rows = conn.execute(query, params).fetchall()

        features = []
        for row in rows:
            if row.geojson:
                geom = json.loads(row.geojson)
                features.append({
                    "type": "Feature",
                    "geometry": geom,
                    "properties": {
                        "osm_id": row.osm_id,
                        "name": row.name,
                        "amenity": row.amenity,
                        "shop": row.shop,
                        "lat": round(float(row.lat), 6) if row.lat else None,
                        "lng": round(float(row.lng), 6) if row.lng else None,
                    },
                })

        return {
            "success": True,
            "type": "FeatureCollection",
            "features": features,
            "count": len(features),
            "bbox": bbox,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def reverse_geocode_postgis(lat: float, lng: float, radius_meters: int = 100) -> dict:
    """
    تبدیل مختصات به آدرس از داده‌های OSM
    """
    if not isinstance(lat, (int, float)) or not isinstance(lng, (int, float)):
        raise ValueError(f"lat/lng باید number باشن")
    
    try:
        query = text("""
            SELECT name, amenity, place, highway,
                ST_Distance(
                    ST_Transform(way, 32639),
                    ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 32639)
                ) as distance_m
            FROM planet_osm_point
            WHERE name IS NOT NULL
                AND ST_DWithin(
                    ST_Transform(way, 32639),
                    ST_Transform(ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), 32639),
                    :radius
                )
            ORDER BY distance_m ASC
            LIMIT 5
        """)

        with engine.connect() as conn:
            rows = conn.execute(query, {"lat": lat, "lng": lng, "radius": radius_meters}).fetchall()

        if not rows:
            return {
                "success": True,
                "found": False,
                "message": f"هیچ مکانی در شعاع {radius_meters} متری پیدا نشد",
                "coordinates": {"lat": lat, "lng": lng},
            }

        nearest = rows[0]
        return {
            "success": True,
            "found": True,
            "name": nearest.name,
            "type": nearest.amenity or nearest.place or nearest.highway,
            "distance_meters": round(float(nearest.distance_m), 2),
            "coordinates": {"lat": lat, "lng": lng},
            "nearby": [
                {
                    "name": r.name,
                    "type": r.amenity or r.place,
                    "distance_m": round(float(r.distance_m), 2),
                }
                for r in rows
            ],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
