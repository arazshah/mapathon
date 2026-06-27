"""
Executor - اجرای مراحل plan با اتصال به geo_tools واقعی
"""
import re
from typing import Any, Dict

# Import کد واقعی از geo_tools
from app.geo_tools.osm import (
    geocode_from_postgis,
    osm_spatial_query,
    reverse_geocode_postgis,
)
from app.geo_tools.geometry import (
    calculate_distance,
    create_buffer,
    calculate_area,
    check_point_in_polygon,
    find_intersection,
)


def execute_plan(plan: Dict[str, Any]) -> Dict[str, Any]:
    """اجرای مراحل plan"""
    context = {}
    steps_results = []

    for step_config in plan.get("steps", []):
        step_num = step_config.get("step", 0)
        tool_name = step_config.get("tool", "").lower()
        params = step_config.get("params", {})
        save_as = step_config.get("save_as", "")

                try:
            # نرمال‌سازی آکولادها به فرمت استاندارد متغیرها
            params = _normalize_braces(params)
            # جایگزینی متغیرها
            params = _substitute_variables(params, context)

            # اجرای ابزار
            result = _execute_tool(tool_name, params)

            if not result.get("success", False):
                return {
                    "success": False,
                    "error": f"قدم {step_num} شکست خورد: {result.get('error', 'خطای نامشخص')}",
                    "debug": {"plan": plan, "steps": steps_results},
                }

            if save_as:
                context[save_as] = result

            steps_results.append({
                "step": step_num,
                "tool": tool_name,
                "description": step_config.get("description", ""),
                "save_as": save_as,
                "success": True,
                "result": result,
            })

        except Exception as e:
            return {
                "success": False,
                "error": f"قدم {step_num} شکست خورد: {str(e)}",
                "debug": {"plan": plan, "steps": steps_results},
            }

    try:
        template = plan.get("final_answer_template", "")
        # اگر template متغیرهای ناشناخته داشت، با context واقعی جایگزین کن
        template = _fix_template_vars(template, context)
        final_answer = _generate_answer(template, context)
    except Exception as e:
        final_answer = f"خطا در ایجاد پاسخ: {str(e)}"

    return {
        "success": True,
        "steps": steps_results,
        "context": context,
        "answer": final_answer,
    }


def _normalize_braces(obj: Any) -> Any:
    """تبدیل {var.path} به $var.path در مقادیر params (خطای رایج LLM)"""
    import re
    if isinstance(obj, str):
        # فقط اگر کل رشته یک placeholder آکولادی است
        m = re.fullmatch(r'\{([a-zA-Z_][a-zA-Z0-9_.\[\]]*)\}', obj.strip())
        if m:
            return "$" + m.group(1)
        return obj
    elif isinstance(obj, dict):
        return {k: _normalize_braces(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_braces(i) for i in obj]
    return obj


def _normalize_braces(obj: Any) -> Any:
    """تبدیل {var.path} به $var.path در مقادیر params (خطای رایج LLM)"""
    import re
    if isinstance(obj, str):
        # فقط اگر کل رشته یک placeholder آکولادی است
        m = re.fullmatch(r'\{([a-zA-Z_][a-zA-Z0-9_.\[\]]*)\}', obj.strip())
        if m:
            return "$" + m.group(1)
        return obj
    elif isinstance(obj, dict):
        return {k: _normalize_braces(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_normalize_braces(i) for i in obj]
    return obj


def _substitute_variables(obj: Any, context: Dict[str, Any]) -> Any:
    """
    جایگزینی $variable.path با مقدار واقعی
    خروجی عددی → عدد می‌مونه (نه string)
    """
    if isinstance(obj, str):
        # اگر کل string فقط یک متغیر است → مقدار اصلی (با نوع) برگردون
        full_match = re.fullmatch(
            r'\$([a-zA-Z_][a-zA-Z0-9_]*(?:(?:\.[a-zA-Z_][a-zA-Z0-9_]*)|(?:\[\d+\]))*)', obj
        )
        if full_match:
            value = _get_nested_value(context, full_match.group(1))
            if value is None:
                raise ValueError(f"متغیر ${full_match.group(1)} پیدا نشد")
            return value  # حفظ نوع (float/int/dict)

        # وگرنه string replacement
        pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*(?:(?:\.[a-zA-Z_][a-zA-Z0-9_]*)|(?:\[\d+\]))*)'
        def replacer(match):
            value = _get_nested_value(context, match.group(1))
            if value is None:
                raise ValueError(f"متغیر ${match.group(1)} پیدا نشد")
            return str(value)
        return re.sub(pattern, replacer, obj)

    elif isinstance(obj, dict):
        return {k: _substitute_variables(v, context) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_substitute_variables(item, context) for item in obj]
    return obj


def _get_nested_value(obj: Any, path: str) -> Any:
    """
    دریافت مقدار nested مثل:
    - best_match.lat
    - features[0].geometry.coordinates[1]
    """
    # Parse path: pharmacy_location.features[0].geometry.coordinates[1]
    import re
    
    # Split by . but keep [index] intact
    parts = re.split(r'(?<!\[)\.(?!\d)', path)
    
    current = obj
    for part in parts:
        if current is None:
            return None
        
        # بررسی اگر part شامل [index] باشه
        match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)((?:\[\d+\])+)', part)
        if match:
            key = match.group(1)
            indices = re.findall(r'\[(\d+)\]', match.group(2))
            
            # دسترسی به key
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return None
            
            # دسترسی به indices
            for idx in indices:
                if isinstance(current, (list, tuple)):
                    try:
                        current = current[int(idx)]
                    except (IndexError, ValueError):
                        return None
                else:
                    return None
        else:
            # بدون index
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
    
    return current


def _execute_tool(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """اجرای ابزار با نگاشت به توابع واقعی geo_tools"""

    if tool_name == "geocode":
        return geocode_from_postgis(**params)

    elif tool_name == "reverse_geocode":
        return reverse_geocode_postgis(**params)

    elif tool_name == "osm_search":
        return osm_spatial_query(**params)

    elif tool_name == "calculate_distance":
        return calculate_distance(**params)

    elif tool_name == "calculate_area":
        import json
        # LLM گاهی اسم پارامتر را اشتباه می‌گذارد - نرمال‌سازی
        geom = (params.get("geometry_geojson")
                or params.get("geojson")
                or params.get("geometry")
                or params.get("polygon_geojson"))

        # اگر کل best_match dict آمده، فیلد geojson را بکش بیرون
        if isinstance(geom, dict) and "geojson" in geom and "type" not in geom:
            geom = geom["geojson"]

        # اگر string است، parse کن
        if isinstance(geom, str):
            try:
                geom = json.loads(geom)
            except Exception:
                return {"success": False, "error": "geometry_geojson باید JSON معتبر باشد"}

        if not isinstance(geom, dict):
            return {"success": False, "error": "هندسه‌ای برای محاسبه مساحت یافت نشد"}

        # اگر geometry از نوع Point است، مساحت ندارد
        if geom.get("type") == "Point":
            return {"success": False, "error": "این مکان یک نقطه است و مساحت ندارد (باید polygon باشد)"}

        return calculate_area(geometry_geojson=geom)

    elif tool_name == "create_buffer":
        return create_buffer(**params)

    elif tool_name == "point_in_polygon":
        return check_point_in_polygon(**params)

    elif tool_name == "find_intersection":
        return find_intersection(**params)

    else:
        return {"success": False, "error": f"ابزار نامعروف: {tool_name}"}


def _generate_answer(template: str, context: Dict[str, Any]) -> str:
    """تولید پاسخ نهایی"""
    pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*(?:(?:\.[a-zA-Z_][a-zA-Z0-9_]*)|(?:\[\d+\]))*)\}'

    def replacer(match):
        value = _get_nested_value(context, match.group(1))
        if value is None:
            return f"[{match.group(1)}]"
        if isinstance(value, dict):
            if "distance_display" in value:
                return value["distance_display"]
            if "best_match" in value and isinstance(value["best_match"], dict):
                bm = value["best_match"]
                return f"{bm.get('name', '')} ({bm.get('lat')}, {bm.get('lng')})"
            if "count" in value:
                return str(value["count"])
        return str(value)

    return re.sub(pattern, replacer, template)


def _fix_template_vars(template: str, context: dict) -> str:
    """
    اگر LLM اسم متغیر اشتباه گذاشته، با متغیر واقعی موجود در context جایگزین کن
    مثلاً {distance_result.distance_display} → {distance_azadi_vanak.distance_display}
    """
    import re
    placeholders = re.findall(r'\{([^}]+)\}', template)
    
    for ph in placeholders:
        # Parse path
        parts = re.split(r'(?<!\[)\.(?!\d)', ph)
        root_var = parts[0]
        
        # اگر root_var در context موجود نیست، جایگزین پیدا کن
        if root_var not in context:
            suffix = ".".join(parts[1:]) if len(parts) > 1 else ""
            
            # دنبال متغیری بگرد که همون suffix رو داشته باشه
            for ctx_key, ctx_val in context.items():
                if not isinstance(ctx_val, dict):
                    continue
                
                if suffix:
                    # بررسی کن که مقدار nested وجود داره
                    check = _get_nested_value(ctx_val, suffix)
                    if check is not None:
                        new_ph = f"{ctx_key}.{suffix}"
                        template = template.replace(f"{{{ph}}}", f"{{{new_ph}}}")
                        break
                else:
                    # بدون suffix — خود متغیر رو جایگزین کن
                    template = template.replace(f"{{{ph}}}", f"{{{ctx_key}}}")
                    break
    
    return template
