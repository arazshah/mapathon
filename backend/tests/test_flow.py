"""
تست‌های end-to-end برای flow کامل
"""
import pytest
from app.core.llm_planner import create_plan, _clean_query
from app.core.executor import execute_plan, _run_tool
from app.core.response_builder import build_response


# ─── تست‌های llm_planner ───────────────────────────────────────

class TestCleanQuery:
    def test_removes_kojast(self):
        assert _clean_query("آزادی کجاست") == "آزادی"

    def test_removes_kojast_vanak(self):
        assert _clean_query("ونک کجاست") == "ونک"

    def test_keeps_pure_name(self):
        """نام خالص بدون کلمه سوالی دست نخورد"""
        result = _clean_query("آزادی")
        assert "آزادی" in result

    def test_empty_fallback(self):
        """اگه بعد از تمیزکاری چیزی نموند، متن اصلی برگرده"""
        result = _clean_query("کجاست")
        assert result  # نباید خالی باشد

    def test_removes_question_mark(self):
        assert "؟" not in _clean_query("آزادی کجاست؟")
        assert "?" not in _clean_query("where is azadi?")


class TestCreatePlan:
    def test_restaurant_plan(self):
        plan = create_plan("رستوران‌های تهران")
        assert "steps" in plan
        assert plan["steps"][0]["tool"] == "osm_search"
        assert plan["steps"][0]["params"]["osm_tags"] == {"amenity": "restaurant"}

    def test_hospital_isfahan(self):
        plan = create_plan("بیمارستان‌های اصفهان")
        assert plan["steps"][0]["tool"] == "osm_search"
        assert plan["steps"][0]["params"]["osm_tags"] == {"amenity": "hospital"}
        # bbox باید اصفهان باشد (lng > 51)
        bbox = plan["steps"][0]["params"]["bbox"]
        assert bbox[0] > 51.0

    def test_distance_plan_has_3_steps(self):
        plan = create_plan("فاصله آزادی تا ونک")
        tools = [s["tool"] for s in plan["steps"]]
        assert "geocode" in tools
        assert "calculate_distance" in tools
        assert len(plan["steps"]) == 3

    def test_geocode_plan_clean_address(self):
        plan = create_plan("آزادی کجاست")
        assert plan["steps"][0]["tool"] == "geocode"
        # آدرس باید تمیز شده باشد
        addr = plan["steps"][0]["params"]["address"]
        assert "کجاست" not in addr
        assert addr.strip() != ""

    def test_distance_plan_saves_results(self):
        plan = create_plan("فاصله تهران به اصفهان")
        save_names = [s["save_as"] for s in plan["steps"]]
        # هر step باید save_as داشته باشد
        assert all(name for name in save_names)


# ─── تست‌های executor ──────────────────────────────────────────

class TestRunTool:
    def test_calculate_distance_returns_success(self):
        result = _run_tool("calculate_distance", {
            "lat1": 35.6997, "lng1": 51.3380,
            "lat2": 35.7572, "lng2": 51.4100,
        })
        assert result["success"]
        assert result["distance_km"] > 0
        assert result["distance_meters"] > 0

    def test_calculate_distance_reasonable_range(self):
        """فاصله دو نقطه در تهران باید بین ۱ تا ۵۰ کیلومتر باشد"""
        result = _run_tool("calculate_distance", {
            "lat1": 35.6997, "lng1": 51.3380,
            "lat2": 35.7572, "lng2": 51.4100,
        })
        assert result["success"]
        assert 1.0 < result["distance_km"] < 50.0

    def test_unknown_tool(self):
        result = _run_tool("nonexistent_tool", {})
        assert not result["success"]
        assert "وجود ندارد" in result["error"]

    def test_all_11_tools_registered(self):
        import inspect, re
        src = inspect.getsource(_run_tool)
        expected = [
            "calculate_distance", "geocode", "reverse_geocode",
            "osm_search", "calculate_area", "create_buffer",
            "point_in_polygon", "find_intersection",
            "find_nearest_point", "get_bbox", "reproject_geometry",
        ]
        for tool in expected:
            assert f'"{tool}"' in src, f"ابزار '{tool}' ثبت نشده!"


class TestExecutePlan:
    def test_distance_chain(self):
        plan = {
            "steps": [
                {
                    "step": 1, "tool": "calculate_distance",
                    "params": {
                        "lat1": 35.6997, "lng1": 51.3380,
                        "lat2": 35.7572, "lng2": 51.4100,
                    },
                    "save_as": "result",
                }
            ],
            "final_answer_template": "فاصله {result.distance_km} کیلومتر",
        }
        result = execute_plan(plan)
        assert result["success"]
        assert "result" in result["context"]
        assert result["context"]["result"]["distance_km"] > 0

    def test_empty_plan(self):
        result = execute_plan({"steps": []})
        assert not result["success"]

    def test_template_substitution(self):
        plan = {
            "steps": [
                {
                    "step": 1, "tool": "calculate_distance",
                    "params": {
                        "lat1": 35.6997, "lng1": 51.3380,
                        "lat2": 35.7572, "lng2": 51.4100,
                    },
                    "save_as": "dist",
                }
            ],
            "final_answer_template": "{dist.distance_km}",
        }
        result = execute_plan(plan)
        assert result["success"]
        assert result["context"]["dist"]["success"]


# ─── تست‌های response_builder ──────────────────────────────────

class TestBuildResponse:
    def _exec_ok(self, context, template=""):
        return {
            "success": True, "context": context,
            "final_template": template, "step_results": [],
        }

    def test_distance_report(self):
        ctx = {
            "dist": {
                "success": True,
                "distance_km": 7.443,
                "distance_meters": 7443.3,
                "point1": {"lat": 35.69, "lng": 51.33},
                "point2": {"lat": 35.75, "lng": 51.41},
            }
        }
        resp = build_response("فاصله x تا y", {}, self._exec_ok(ctx))
        assert resp["success"]
        assert resp["report"]["type"] == "distance"
        assert resp["report"]["distance_km"] == 7.443

    def test_list_report(self):
        ctx = {
            "restaurants": {
                "success": True,
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [51.5, 35.7]},
                        "properties": {
                            "name": "رستوران تست",
                            "amenity": "restaurant",
                            "lat": 35.7, "lng": 51.5,
                        },
                    }
                ],
                "count": 1,
            }
        }
        resp = build_response("رستوران", {}, self._exec_ok(ctx))
        assert resp["success"]
        assert resp["report"]["type"] == "list"
        assert resp["report"]["count"] == 1
        assert resp["map"]["count"] == 1
        assert resp["map"]["zoom"] >= 11

    def test_failed_exec(self):
        resp = build_response("تست", {}, {
            "success": False, "error": "خطای تست",
        })
        assert not resp["success"]
        assert resp["error"] == "خطای تست"
        assert resp["map"] is None

    def test_answer_template_substitution(self):
        ctx = {"r": {"distance_km": 5.5}}
        resp = build_response(
            "فاصله", {},
            self._exec_ok(ctx, "{r.distance_km} کیلومتر"),
        )
        assert resp["answer"] == "5.5 کیلومتر"

    def test_map_has_required_keys(self):
        ctx = {
            "res": {
                "success": True, "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [51.5, 35.7]},
                        "properties": {"name": "تست", "amenity": "cafe",
                                       "lat": 35.7, "lng": 51.5},
                    }
                ],
                "count": 1,
            }
        }
        resp = build_response("تست", {}, self._exec_ok(ctx))
        assert resp["map"] is not None
        assert "geojson" in resp["map"]
        assert "center" in resp["map"]
        assert "zoom" in resp["map"]
        assert "count" in resp["map"]
