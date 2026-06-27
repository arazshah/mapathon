"""
ساخت خروجی استاندارد برای frontend
هر query → answer + map + report
"""
import re


def build_response(question: str, plan: dict, exec_result: dict) -> dict:
    """تبدیل نتیجه خام executor به contract استاندارد"""
    if not exec_result.get("success"):
        return {
            "success": False,
            "question": question,
            "answer": None,
            "map": None,
            "report": None,
            "error": exec_result.get("error"),
            "debug": {"plan": plan, "steps": exec_result.get("step_results")},
        }

    context = exec_result.get("context", {})
    answer = exec_result.get("answer") or _build_answer(exec_result.get("final_template", ""), context)
    map_data = _build_map(context)
    report = _build_report(context)

    return {
        "success": True,
        "question": question,
        "answer": answer,
        "map": map_data,
        "report": report,
        "error": None,
        "debug": {"plan": plan, "steps": exec_result.get("step_results")},
    }


def _build_answer(template: str, context: dict) -> str:
    """جایگزینی {var.field} با مقادیر واقعی"""
    if not template:
        return "پاسخ آماده است"
    answer = template
    for ph in re.findall(r"\{([^}]+)\}", template):
        val = _get_nested(context, ph)
        answer = answer.replace(f"{{{ph}}}", str(val) if val is not None else "?")
    return answer


def _build_map(context: dict) -> dict | None:
    """استخراج geojson + محاسبه center و zoom برای MapLibre"""
    features = []
    for val in context.values():
        if not isinstance(val, dict):
            continue
        # FeatureCollection (osm_search)
        if val.get("type") == "FeatureCollection":
            features.extend(val.get("features", []))
        # geocode results
        elif "results" in val and isinstance(val["results"], list):
            for r in val["results"]:
                if r.get("geojson"):
                    features.append({
                        "type": "Feature",
                        "geometry": r["geojson"],
                        "properties": {"name": r.get("name"), "type": r.get("type")},
                    })
        # نتیجه هندسی تک (buffer/intersection)
        elif val.get("geometry"):
            features.append({
                "type": "Feature",
                "geometry": val["geometry"],
                "properties": {"computed": True},
            })

    if not features:
        return None

    center, zoom = _compute_view(features)
    return {
        "geojson": {"type": "FeatureCollection", "features": features},
        "center": center,
        "zoom": zoom,
        "count": len(features),
    }


def _build_report(context: dict) -> dict | None:
    """ساخت گزارش متناسب با نوع نتیجه: distance / list / area / stat"""
    for val in context.values():
        if not isinstance(val, dict):
            continue

        # فاصله
        if "distance_km" in val:
            return {
                "type": "distance",
                "distance_km": val["distance_km"],
                "distance_meters": val.get("distance_meters"),
                "point1": val.get("point1"),
                "point2": val.get("point2"),
            }

        # مساحت
        if "area_km2" in val:
            return {
                "type": "area",
                "area_m2": val.get("area_m2"),
                "area_hectares": val.get("area_hectares"),
                "area_km2": val.get("area_km2"),
            }

        # لیست مکان‌ها (osm_search)
        if val.get("type") == "FeatureCollection":
            items = [
                {
                    "name": f["properties"].get("name") or "بدون نام",
                    "type": f["properties"].get("amenity") or f["properties"].get("shop"),
                    "lat": f["properties"].get("lat"),
                    "lng": f["properties"].get("lng"),
                }
                for f in val.get("features", [])
            ]
            return {"type": "list", "count": val.get("count", len(items)), "items": items}

    return None


def _compute_view(features: list) -> tuple:
    """محاسبه center و zoom از مجموعه نقاط"""
    lngs, lats = [], []
    for f in features:
        geom = f.get("geometry", {})
        coords = geom.get("coordinates")
        if geom.get("type") == "Point" and coords:
            lngs.append(coords[0])
            lats.append(coords[1])

    if not lngs:
        return [51.389, 35.6892], 11  # پیش‌فرض تهران

    center = [sum(lngs) / len(lngs), sum(lats) / len(lats)]
    span = max(max(lngs) - min(lngs), max(lats) - min(lats))
    if span < 0.01:
        zoom = 15
    elif span < 0.05:
        zoom = 13
    elif span < 0.2:
        zoom = 11
    else:
        zoom = 9
    return center, zoom


def _get_nested(data: dict, path: str):
    """دسترسی به مقدار nested: location.best_match.lat"""
    current = data
    for k in path.split("."):
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current
