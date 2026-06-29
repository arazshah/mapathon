from sqlalchemy import text

# نگاشت نوع موجودیت به شرط‌های جستجو
# هر موجودیت: (شرط ستون مستقیم, شرط tags)
ENTITY_CONDITIONS = {
    "metro": {
        "direct": "station = 'subway' OR railway = 'subway_entrance'",
        "tags": "tags->'station' = 'subway' OR tags->'railway' = 'subway_entrance'",
    },
    "subway": {
        "direct": "station = 'subway'",
        "tags": "tags->'station' = 'subway'",
    },
    "restaurant": {
        "direct": "amenity = 'restaurant'",
        "tags": "tags->'amenity' = 'restaurant'",
    },
    "pharmacy": {
        "direct": "amenity = 'pharmacy'",
        "tags": "tags->'amenity' = 'pharmacy'",
    },
    "hospital": {
        "direct": "amenity = 'hospital'",
        "tags": "tags->'amenity' = 'hospital'",
    },
    "park": {
        "direct": "leisure = 'park'",
        "tags": "tags->'leisure' = 'park'",
    },
    "school": {
        "direct": "amenity = 'school'",
        "tags": "tags->'amenity' = 'school'",
    },
    "cafe": {
        "direct": "amenity = 'cafe'",
        "tags": "tags->'amenity' = 'cafe'",
    },
    "bank": {
        "direct": "amenity = 'bank'",
        "tags": "tags->'amenity' = 'bank'",
    },
    "fuel": {
        "direct": "amenity = 'fuel'",
        "tags": "tags->'amenity' = 'fuel'",
    },
    "atm": {
        "direct": "amenity = 'atm'",
        "tags": "tags->'amenity' = 'atm'",
    },
    "bus_stop": {
        "direct": "highway = 'bus_stop'",
        "tags": "tags->'highway' = 'bus_stop'",
    },
    "supermarket": {
        "direct": "shop = 'supermarket'",
        "tags": "tags->'shop' = 'supermarket'",
    },
    "hotel": {
        "direct": "tourism = 'hotel'",
        "tags": "tags->'tourism' = 'hotel'",
    },
}


def _get_columns(db) -> set:
    """دریافت ستون‌های موجود در planet_osm_point"""
    sql = text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'planet_osm_point'
    """)
    rows = db.execute(sql).fetchall()
    return {r[0] for r in rows}


def _build_entity_condition(entity_type: str, has_direct_cols: bool) -> str:
    """
    ساخت شرط SQL برای نوع موجودیت.
    اگر ستون‌های مستقیم (amenity, shop...) وجود دارند، از آن‌ها استفاده می‌کند.
    در غیر این صورت از tags استفاده می‌کند.
    """
    cond = ENTITY_CONDITIONS.get(entity_type)
    if not cond:
        return f"name ILIKE '%{entity_type}%'"

    if has_direct_cols:
        # ترکیب هر دو برای اطمینان
        return f"({cond['direct']} OR {cond['tags']})"
    else:
        return f"({cond['tags']})"


def geocode_place(db, name: str) -> dict | None:
    """
    جستجوی مکان در OSM با اولویت‌بندی هوشمند.
    """
    # جستجوی دقیق در polygon (بزرگ‌ترین)
    sql = text("""
        SELECT 
            osm_id, name, tags,
            ST_Y(ST_Centroid(ST_Transform(way, 4326))) as lat,
            ST_X(ST_Centroid(ST_Transform(way, 4326))) as lon
        FROM planet_osm_polygon
        WHERE name = :exact_name
        ORDER BY ST_Area(way) DESC
        LIMIT 1
    """)
    result = db.execute(sql, {"exact_name": name}).mappings().first()
    if result and result["lat"] is not None:
        return _build_place(result, "polygon")

    # جستجوی دقیق در point
    sql = text("""
        SELECT osm_id, name, tags,
            ST_Y(ST_Transform(way, 4326)) as lat,
            ST_X(ST_Transform(way, 4326)) as lon
        FROM planet_osm_point
        WHERE name = :exact_name
        LIMIT 1
    """)
    result = db.execute(sql, {"exact_name": name}).mappings().first()
    if result and result["lat"] is not None:
        return _build_place(result, "point")

    # جستجوی ILIKE در polygon
    sql = text("""
        SELECT osm_id, name, tags,
            ST_Y(ST_Centroid(ST_Transform(way, 4326))) as lat,
            ST_X(ST_Centroid(ST_Transform(way, 4326))) as lon
        FROM planet_osm_polygon
        WHERE name ILIKE :name
        ORDER BY ST_Area(way) DESC
        LIMIT 1
    """)
    result = db.execute(sql, {"name": f"%{name}%"}).mappings().first()
    if result and result["lat"] is not None:
        return _build_place(result, "polygon")

    # جستجوی ILIKE در point
    sql = text("""
        SELECT osm_id, name, tags,
            ST_Y(ST_Transform(way, 4326)) as lat,
            ST_X(ST_Transform(way, 4326)) as lon
        FROM planet_osm_point
        WHERE name ILIKE :name
        LIMIT 1
    """)
    result = db.execute(sql, {"name": f"%{name}%"}).mappings().first()
    if result and result["lat"] is not None:
        return _build_place(result, "point")

    return None


def find_pois_near(
    db,
    entity_type: str,
    lat: float,
    lon: float,
    radius_meters: int,
    limit: int = 30,
) -> list:
    """
    جستجوی POI نزدیک یک نقطه — با دو روش موازی برای حداکثر پوشش.
    """
    # بررسی ستون‌های موجود
    columns = _get_columns(db)
    has_direct = "amenity" in columns

    entity_cond = _build_entity_condition(entity_type, has_direct)

    # روش اول: ST_DWithin با geography (دقیق، بر حسب متر)
    sql = text(f"""
        SELECT 
            osm_id, name, tags,
            ST_Y(ST_Transform(way, 4326)) as lat,
            ST_X(ST_Transform(way, 4326)) as lon,
            ST_Distance(
                ST_Transform(way, 4326)::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography
            ) as distance_meters
        FROM planet_osm_point
        WHERE {entity_cond}
          AND ST_DWithin(
                ST_Transform(way, 4326)::geography,
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                :radius
          )
        ORDER BY distance_meters
        LIMIT :limit
    """)

    try:
        rows = db.execute(sql, {
            "lat": lat, "lon": lon,
            "radius": radius_meters,
            "limit": limit,
        }).mappings().all()
    except Exception as e:
        print(f"[find_pois_near] ST_DWithin failed: {e}")
        rows = []

    # اگر نتیجه نداشت، روش دوم: بدون geography (با درجه)
    if not rows:
        deg = radius_meters / 111000.0  # تبدیل تقریبی متر به درجه
        sql2 = text(f"""
            SELECT 
                osm_id, name, tags,
                ST_Y(ST_Transform(way, 4326)) as lat,
                ST_X(ST_Transform(way, 4326)) as lon,
                ST_Distance(
                    ST_Transform(way, 4326),
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                ) * 111000 as distance_meters
            FROM planet_osm_point
            WHERE {entity_cond}
              AND ST_DWithin(
                    ST_Transform(way, 4326),
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                    :deg
              )
            ORDER BY distance_meters
            LIMIT :limit
        """)
        try:
            rows = db.execute(sql2, {
                "lat": lat, "lon": lon,
                "deg": deg,
                "limit": limit,
            }).mappings().all()
        except Exception as e:
            print(f"[find_pois_near] fallback failed: {e}")
            rows = []

    # اگر باز هم نتیجه نداشت، شعاع را ۳ برابر کن
    if not rows:
        print(f"[find_pois_near] No results, expanding radius to {radius_meters * 3}m")
        deg = (radius_meters * 3) / 111000.0
        sql3 = text(f"""
            SELECT 
                osm_id, name, tags,
                ST_Y(ST_Transform(way, 4326)) as lat,
                ST_X(ST_Transform(way, 4326)) as lon,
                ST_Distance(
                    ST_Transform(way, 4326),
                    ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
                ) * 111000 as distance_meters
            FROM planet_osm_point
            WHERE {entity_cond}
            ORDER BY ST_Distance(
                ST_Transform(way, 4326),
                ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)
            )
            LIMIT :limit
        """)
        try:
            rows = db.execute(sql3, {
                "lat": lat, "lon": lon,
                "limit": limit,
            }).mappings().all()
        except Exception as e:
            print(f"[find_pois_near] expand radius failed: {e}")
            rows = []

    results = []
    for row in rows:
        if row["lat"] is None:
            continue
        results.append({
            "osm_id": row["osm_id"],
            "name": row["name"] or "بدون نام",
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "distance_meters": round(float(row["distance_meters"])),
            "tags": dict(row["tags"]) if row["tags"] else {},
        })

    return results


def find_entity_by_name(db, entity_type: str, name: str) -> list:
    """جستجوی مستقیم موجودیت بر اساس نام"""
    columns = _get_columns(db)
    has_direct = "amenity" in columns
    entity_cond = _build_entity_condition(entity_type, has_direct)

    sql = text(f"""
        SELECT 
            osm_id, name, tags,
            ST_Y(ST_Transform(way, 4326)) as lat,
            ST_X(ST_Transform(way, 4326)) as lon
        FROM planet_osm_point
        WHERE {entity_cond}
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


def distance_between_places(db, name1: str, name2: str) -> dict | None:
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
    sql = text("""
        SELECT 
            osm_id, name, tags,
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


def _build_place(result, source: str) -> dict:
    return {
        "osm_id": result["osm_id"],
        "name": result["name"],
        "lat": float(result["lat"]),
        "lon": float(result["lon"]),
        "source": source,
        "tags": dict(result["tags"]) if result["tags"] else {},
    }
