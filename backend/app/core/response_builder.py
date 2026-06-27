"""
ساخت خروجی استاندارد برای frontend
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
    template = exec_result.get("final_template", "")
    answer = exec_result.get("answer") or _build_answer(template, context)
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
    """
    جایگزینی placeholder ها با مقادیر واقعی
    پشتیبانی از: {var.field} و [var.field] و {var}
    """
    if not template:
        return "پاسخ آماده است"

    answer = template

    # ۱. تبدیل [var.field] به {var.field} (LLM گاهی این فرمت می‌فرسته)
    answer = re.sub(r'\[([^\]]+)\]', r'{\1}', answer)

    # ۲. جایگزینی {var.field.subfield}
    for ph in re.findall(r"\{([^}]+)\}", answer):
        val = _get_nested(context, ph)
        if val is not None:
            # اگر dict بود → فرمت کن
            if isinstance(val, dict):
                formatted = _format_dict_value(ph, val)
            else:
                formatted = str(val)
            answer = answer.replace(f"{{{ph}}}", formatted)
        else:
            # placeholder حل نشد → نشانه سوال
            answer = answer.replace(f"{{{ph}}}", "?")

    return answer


def _format_dict_value(key: str, val: dict) -> str:
    """تبدیل dict به رشته خوانا"""
    # مساحت
    if "area_m2" in val:
        m2 = val.get("area_m2", 0)
        ha = val.get("area_hectares", 0)
        return f"{m2:,.1f} متر مربع ({ha:.2f} هکتار)"
    # فاصله
    if "distance_km" in val:
        return val.get("distance_display", f"{val['distance_km']:.2f} کیلومتر")
    # geocode best_match
    if "best_match" in val:
        bm = val["best_match"]
        return bm.get("name", str(val))
    # نتیجه bool
    if "inside" in val:
        return "بله، داخل است" if val["inside"] else "خیر، خارج است"
    # پیش‌فرض
    return str(val)


def _build_map(context: dict) -> dict | None:
    """استخراج geojson + محاسبه center و zoom"""
    features = []
    for val in context.values():
        if not isinstance(val, dict):
            continue
        if val.get("type") == "FeatureCollection":
            features.extend(val.get("features", []))
        elif "results" in val and isinstance(val["results"], list):
            for r in val["results"]:
                if r.get("geojson"):
                    features.append({
                        "type": "Feature",
                        "geometry": r["geojson"],
                        "properties": {"name": r.get("name"), "type": r.get("type")},
                    })
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
    """ساخت گزارش متناسب با نوع نتیجه"""
    for val in context.values():
        if not isinstance(val, dict):
            continue
        if "distance_km" in val:
            return {
                "type": "distance",
                "distance_km": val["distance_km"],
                "distance_meters": val.get("distance_m"),
                "display": val.get("distance_display"),
            }
        if "area_km2" in val:
            return {
                "type": "area",
                "area_m2": val.get("area_m2"),
                "area_hectares": val.get("area_hectares"),
                "area_km2": val.get("area_km2"),
            }
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
        if "inside" in val:
            return {
                "type": "point_in_polygon",
                "inside": val["inside"],
                "polygon_area_m2": val.get("polygon_area_m2"),
            }
    return None


def _compute_view(features: list) -> tuple:
    """محاسبه center و zoom"""
    lngs, lats = [], []
    for f in features:
        geom = f.get("geometry", {})
        coords = geom.get("coordinates")
        if geom.get("type") == "Point" and coords:
            lngs.append(coords[0])
            lats.append(coords[1])

    if not lngs:
        return [51.389, 35.6892], 11

    center = [sum(lngs) / len(lngs), sum(lats) / len(lats)]
    span = max(max(lngs) - min(lngs), max(lats) - min(lats))
    zoom = 15 if span < 0.01 else 13 if span < 0.05 else 11 if span < 0.2 else 9
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
