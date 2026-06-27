"""
ابزارهای هندسی خالص - بدون نیاز به دیتابیس
از Shapely و PyProj استفاده می‌کند
"""
from shapely.geometry import shape, Point, mapping
from shapely.ops import transform
from pyproj import Transformer, CRS
import json


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> dict:
    """
    محاسبه فاصله بین دو نقطه
    ورودی: مختصات جغرافیایی (WGS84)
    خروجی: فاصله به متر و کیلومتر
    """
    try:
        # اطمینان از scalar بودن مختصات (LLM گاهی None یا string می‌فرستد)
        def _to_float(v, name):
            if v is None:
                raise ValueError(f"{name} مقدار ندارد (None) - احتمالاً مکان پیدا نشد")
            if isinstance(v, (list, tuple)):
                raise ValueError(f"{name} باید عدد باشد نه لیست")
            return float(v)

        lat1 = _to_float(lat1, "lat1")
        lng1 = _to_float(lng1, "lng1")
        lat2 = _to_float(lat2, "lat2")
        lng2 = _to_float(lng2, "lng2")

        # تبدیل به سیستم متریک ایران (UTM Zone 39N)
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:32639", always_xy=True)
        
        x1, y1 = transformer.transform(lng1, lat1)
        x2, y2 = transformer.transform(lng2, lat2)
        
        point1 = Point(x1, y1)
        point2 = Point(x2, y2)
        
        distance_meters = point1.distance(point2)
        
        km = round(distance_meters / 1000, 3)
        return {
            "success": True,
            "distance_meters": round(distance_meters, 2),
            "distance_km": km,
            "distance_display": f"{km} کیلومتر",
            "point1": {"lat": lat1, "lng": lng1},
            "point2": {"lat": lat2, "lng": lng2},
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_buffer(geometry_geojson: dict, distance_meters: float) -> dict:
    """
    ایجاد منطقه بافر اطراف یک هندسه
    ورودی: GeoJSON geometry + فاصله به متر
    خروجی: polygon بافر به صورت GeoJSON
    """
    try:
        geom = shape(geometry_geojson)
        
        # تبدیل به متریک برای بافر دقیق
        to_metric = Transformer.from_crs("EPSG:4326", "EPSG:32639", always_xy=True)
        to_wgs84 = Transformer.from_crs("EPSG:32639", "EPSG:4326", always_xy=True)
        
        geom_metric = transform(to_metric.transform, geom)
        buffered_metric = geom_metric.buffer(distance_meters)
        buffered_wgs84 = transform(to_wgs84.transform, buffered_metric)
        
        return {
            "success": True,
            "geometry": mapping(buffered_wgs84),
            "distance_meters": distance_meters,
            "area_m2": round(buffered_metric.area, 2),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def calculate_area(geometry_geojson: dict) -> dict:
    """
    محاسبه مساحت یک polygon
    ورودی: GeoJSON geometry
    خروجی: مساحت به متر مربع، هکتار، کیلومتر مربع
    """
    try:
        geom = shape(geometry_geojson)
        
        if geom.geom_type not in ["Polygon", "MultiPolygon"]:
            return {"success": False, "error": "هندسه باید Polygon باشد"}
        
        to_metric = Transformer.from_crs("EPSG:4326", "EPSG:32639", always_xy=True)
        geom_metric = transform(to_metric.transform, geom)
        
        area_m2 = geom_metric.area
        
        return {
            "success": True,
            "area_m2": round(area_m2, 2),
            "area_hectares": round(area_m2 / 10000, 4),
            "area_km2": round(area_m2 / 1_000_000, 6),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_bbox(geometry_geojson: dict) -> dict:
    """
    دریافت محدوده bounding box یک هندسه
    خروجی: [minx, miny, maxx, maxy]
    """
    try:
        geom = shape(geometry_geojson)
        minx, miny, maxx, maxy = geom.bounds
        
        return {
            "success": True,
            "bbox": [minx, miny, maxx, maxy],
            "bbox_dict": {
                "min_lng": minx, "min_lat": miny,
                "max_lng": maxx, "max_lat": maxy,
            },
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def check_point_in_polygon(lat: float, lng: float, polygon_geojson: dict) -> dict:
    """
    بررسی اینکه آیا یک نقطه داخل یک polygon است
    """
    try:
        point = Point(lng, lat)
        polygon = shape(polygon_geojson)
        
        is_inside = polygon.contains(point)
        distance_to_boundary = point.distance(polygon.boundary)
        
        return {
            "success": True,
            "is_inside": is_inside,
            "point": {"lat": lat, "lng": lng},
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_intersection(geom_a_geojson: dict, geom_b_geojson: dict) -> dict:
    """
    پیدا کردن اشتراک دو هندسه
    """
    try:
        geom_a = shape(geom_a_geojson)
        geom_b = shape(geom_b_geojson)
        
        if not geom_a.intersects(geom_b):
            return {
                "success": True,
                "has_intersection": False,
                "geometry": None,
            }
        
        intersection = geom_a.intersection(geom_b)
        
        return {
            "success": True,
            "has_intersection": True,
            "geometry": mapping(intersection),
            "geom_type": intersection.geom_type,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def reproject_geometry(geometry_geojson: dict, target_crs: str) -> dict:
    """
    تبدیل سیستم مختصات یک هندسه
    مثال: EPSG:4326 → EPSG:3857
    """
    try:
        geom = shape(geometry_geojson)
        transformer = Transformer.from_crs("EPSG:4326", target_crs, always_xy=True)
        reprojected = transform(transformer.transform, geom)
        
        return {
            "success": True,
            "geometry": mapping(reprojected),
            "source_crs": "EPSG:4326",
            "target_crs": target_crs,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def find_nearest_point(lat: float, lng: float, geometry_geojson: dict) -> dict:
    """
    پیدا کردن نزدیک‌ترین نقطه روی یک هندسه
    """
    try:
        from shapely.ops import nearest_points
        
        point = Point(lng, lat)
        geom = shape(geometry_geojson)
        
        nearest = nearest_points(point, geom)[1]
        
        to_metric = Transformer.from_crs("EPSG:4326", "EPSG:32639", always_xy=True)
        p1_m = transform(to_metric.transform, point)
        p2_m = transform(to_metric.transform, nearest)
        distance_m = p1_m.distance(p2_m)
        
        return {
            "success": True,
            "nearest_point": {
                "lat": round(nearest.y, 6),
                "lng": round(nearest.x, 6),
            },
            "distance_meters": round(distance_m, 2),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
