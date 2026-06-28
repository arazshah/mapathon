from sqlalchemy import text

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


def geocode_place(db, name: str) -> dict | None:
    """
    جستجوی مکان در داده‌های OSM (PostGIS)
    مختصات مستقیماً از PostGIS با ST_X/ST_Y گرفته می‌شود.
    """
    queries = [
        ("planet_osm_polygon", "ST_Area(way) DESC", "polygon"),
        ("planet_osm_line", "osm_id", "line"),
        ("planet_osm_point", "osm_id", "point"),
    ]

    for table, order_by, source in queries:
        sql = text(f"""
            SELECT 
                osm_id, 
                name, 
                tags,
                ST_Y(ST_Centroid(ST_Transform(way, 4326))) as lat,
                ST_X(ST_Centroid(ST_Transform(way, 4326))) as lon
            FROM {table}
            WHERE name ILIKE :name
            ORDER BY {order_by}
            LIMIT 1
        """)
        result = db.execute(sql, {"name": f"%{name}%"}).mappings().first()
        if result and result["lat"] is not None and result["lon"] is not None:
            return {
                "osm_id": result["osm_id"],
                "name": result["name"],
                "lat": float(result["lat"]),
                "lon": float(result["lon"]),
                "source": source,
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
            ST_Y(ST_Centroid(ST_Transform(way, 4326))) as lat,
            ST_X(ST_Centroid(ST_Transform(way, 4326))) as lon,
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
        if row["lat"] is None or row["lon"] is None:
            continue
        results.append({
            "osm_id": row["osm_id"],
            "name": row["name"],
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
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
        SELECT 
            osm_id, 
            name, 
            tags,
            ST_Y(ST_Centroid(ST_Transform(way, 4326))) as lat,
            ST_X(ST_Centroid(ST_Transform(way, 4326))) as lon,
            ST_Area(ST_Transform(way, 4326)::geography) as area_m2
        FROM planet_osm_polygon
        WHERE name ILIKE :name
        ORDER BY ST_Area(way) DESC
        LIMIT 1
    """)
    result = db.execute(sql, {"name": f"%{name}%"}).mappings().first()

    if not result or result["lat"] is None:
        return None

    return {
        "place": {
            "osm_id": result["osm_id"],
            "name": result["name"],
            "lat": float(result["lat"]),
            "lon": float(result["lon"]),
            "tags": dict(result["tags"]) if result["tags"] else {},
        },
        "area_m2": float(result["area_m2"]),
    }
