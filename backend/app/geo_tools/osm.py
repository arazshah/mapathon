from sqlalchemy import text
from shapely import wkb
from pyproj import Transformer

# تبدیل EPSG:3857 (osm2pgsql) به EPSG:4326
transformer_3857_to_4326 = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)


# نگاشت نوع موجودیت به تگ‌های OSM
ENTITY_TAG_CONDITIONS = {
    "metro": "(tags -> 'railway' = 'station' AND tags -> 'station' = 'subway')",
    "subway": "(tags -> 'railway' = 'station' AND tags -> 'station' = 'subway')",
    "restaurant": "(tags -> 'amenity' = 'restaurant')",
    "pharmacy": "(tags -> 'amenity' = 'pharmacy')",
    "hospital": "(tags -> 'amenity' = 'hospital')",
    "park": "(tags -> 'leisure' = 'park')",
    "school": "(tags -> 'amenity' = 'school')",
    "cafe": "(tags -> 'amenity' = 'cafe')",
    "bank": "(tags -> 'amenity' = 'bank')",
    "fuel": "(tags -> 'amenity' = 'fuel')",
}


def _wkb_to_latlon(wkb_bytes):
    """تبدیل باینری geometry به lat/lon"""
    geom = wkb.loads(wkb_bytes)
    if geom.geom_type == "Point":
        return geom.y, geom.x
    else:
        centroid = geom.centroid
        return centroid.y, centroid.x


def geocode_place(db, name: str) -> dict | None:
    """
    جستجوی مکان در داده‌های OSM محلی (PostGIS)
    """
    # 1. ابتدا در polygon (مناطق، پارک‌ها، محله‌ها)
    sql_polygon = text("""
        SELECT osm_id, name, tags, ST_AsBinary(ST_Transform(way, 4326)) as geom, 'polygon' as source
        FROM planet_osm_polygon
        WHERE name ILIKE :name
        ORDER BY ST_Area(way) DESC
        LIMIT 1
    """)
    result = db.execute(sql_polygon, {"name": f"%{name}%"}).mappings().first()
    if result:
        lat, lon = _wkb_to_latlon(result["geom"])
        return {
            "osm_id": result["osm_id"],
            "name": result["name"],
            "lat": lat,
            "lon": lon,
            "source": "polygon",
            "tags": dict(result["tags"]) if result["tags"] else {},
        }

    # 2. سپس در line (خیابان‌ها، بزرگراه‌ها)
    sql_line = text("""
        SELECT osm_id, name, tags, ST_AsBinary(ST_Transform(way, 4326)) as geom, 'line' as source
        FROM planet_osm_line
        WHERE name ILIKE :name
        LIMIT 1
    """)
    result = db.execute(sql_line, {"name": f"%{name}%"}).mappings().first()
    if result:
        lat, lon = _wkb_to_latlon(result["geom"])
        return {
            "osm_id": result["osm_id"],
            "name": result["name"],
            "lat": lat,
            "lon": lon,
            "source": "line",
            "tags": dict(result["tags"]) if result["tags"] else {},
        }

    # 3. در نهایت در point (نقاط)
    sql_point = text("""
        SELECT osm_id, name, tags, ST_AsBinary(ST_Transform(way, 4326)) as geom, 'point' as source
        FROM planet_osm_point
        WHERE name ILIKE :name
        LIMIT 1
    """)
    result = db.execute(sql_point, {"name": f"%{name}%"}).mappings().first()
    if result:
        lat, lon = _wkb_to_latlon(result["geom"])
        return {
            "osm_id": result["osm_id"],
            "name": result["name"],
            "lat": lat,
            "lon": lon,
            "source": "point",
            "tags": dict(result["tags"]) if result["tags"] else {},
        }

    return None


def find_pois_near(db, entity_type: str, lat: float, lon: float, radius_meters: int, limit: int = 50) -> list:
    """
    جستجوی POI نزدیک یک نقطه خاص
    """
    tag_condition = ENTITY_TAG_CONDITIONS.get(entity_type, "(tags -> 'name' ILIKE :pattern)")

    sql = text(f"""
        SELECT 
            osm_id, 
            name, 
            tags,
            ST_AsBinary(ST_Transform(way, 4326)) as geom,
            ST_Distance(
                ST_Transform(way, 4326)::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) as distance_meters
        FROM planet_osm_point
        WHERE {tag_condition}
          AND ST_DWithin(
                ST_Transform(way, 4326)::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
          )
        ORDER BY distance_meters
        LIMIT :limit
    """)

    params = {
        "lat": lat,
        "lon": lon,
        "radius": radius_meters,
        "limit": limit,
    }

    if entity_type not in ENTITY_TAG_CONDITIONS:
        params["pattern"] = f"%{entity_type}%"

    rows = db.execute(sql, params).mappings().all()

    results = []
    for row in rows:
        p_lat, p_lon = _wkb_to_latlon(row["geom"])
        results.append({
            "osm_id": row["osm_id"],
            "name": row["name"],
            "lat": p_lat,
            "lon": p_lon,
            "distance_meters": round(row["distance_meters"]),
            "tags": dict(row["tags"]) if row["tags"] else {},
        })

    return results


def distance_between_places(db, name1: str, name2: str) -> dict | None:
    """
    محاسبه فاصله بین دو مکان
    """
    place1 = geocode_place(db, name1)
    place2 = geocode_place(db, name2)

    if not place1 or not place2:
        return None

    sql = text("""
        SELECT ST_Distance(
            ST_SetSRID(ST_MakePoint(:lon1, :lat1), 4326)::geography,
            ST_SetSRID(ST_MakePoint(:lon2, :lat2), 4326)::geography
        ) as distance_meters
    """)
    result = db.execute(sql, {
        "lat1": place1["lat"], "lon1": place1["lon"],
        "lat2": place2["lat"], "lon2": place2["lon"],
    }).mappings().first()

    return {
        "from": place1,
        "to": place2,
        "distance_meters": round(result["distance_meters"]),
    }


def area_of_place(db, name: str, entity_type: str | None = None) -> dict | None:
    """
    محاسبه مساحت یک مکان
    """
    sql = text("""
        SELECT osm_id, name, tags, ST_AsBinary(ST_Transform(way, 4326)) as geom,
               ST_Area(ST_Transform(way, 4326)::geography) as area_m2
        FROM planet_osm_polygon
        WHERE name ILIKE :name
        LIMIT 1
    """)
    result = db.execute(sql, {"name": f"%{name}%"}).mappings().first()

    if not result:
        return None

    lat, lon = _wkb_to_latlon(result["geom"])

    return {
        "place": {
            "osm_id": result["osm_id"],
            "name": result["name"],
            "lat": lat,
            "lon": lon,
            "tags": dict(result["tags"]) if result["tags"] else {},
        },
        "area_m2": result["area_m2"],
    }
