"""normalizer 단위 테스트"""
import uuid
import pytest
from parsers.normalizer import normalize_tree, _normalize_fill


class TestNormalizeTree:
    def test_assigns_new_uuid(self, minimal_figma_json):
        from parsers.figma_parser import parse_figma_json
        parsed = parse_figma_json(minimal_figma_json)
        original_id = parsed["id"]
        result = normalize_tree(parsed)

        # 내부 UUID는 새로 생성되어야 함
        assert result["id"] != original_id
        try:
            uuid.UUID(result["id"])
        except ValueError:
            pytest.fail("normalize_tree이 올바른 UUID를 생성하지 않았습니다")

    def test_figma_id_preserved(self, minimal_figma_json):
        from parsers.figma_parser import parse_figma_json
        parsed = parse_figma_json(minimal_figma_json)
        result = normalize_tree(parsed)
        assert result["figmaId"] == "1:1"

    def test_children_each_get_unique_ids(self, minimal_figma_json):
        from parsers.figma_parser import parse_figma_json
        parsed = parse_figma_json(minimal_figma_json)
        result = normalize_tree(parsed)

        root_id = result["id"]
        child_id = result["children"][0]["id"]
        grandchild_id = result["children"][0]["children"][0]["id"]

        assert len({root_id, child_id, grandchild_id}) == 3

    def test_solid_fill_gets_hex_color(self, minimal_figma_json):
        from parsers.figma_parser import parse_figma_json
        parsed = parse_figma_json(minimal_figma_json)
        result = normalize_tree(parsed)

        fill = result["fills"][0]
        assert "hexColor" in fill
        assert fill["hexColor"].startswith("#")
        assert len(fill["hexColor"]) == 7

    def test_non_solid_fill_unchanged(self):
        node = {
            "id": "x:1", "figmaId": "x:1", "name": "Gradient",
            "type": "FRAME",
            "fills": [{"type": "GRADIENT_LINEAR", "gradientStops": []}],
        }
        result = normalize_tree(node)
        fill = result["fills"][0]
        assert "hexColor" not in fill
        assert fill["type"] == "GRADIENT_LINEAR"

    def test_dark_background_hex_value(self):
        """r=0.05, g=0.05, b=0.07 → 약 #0D0D12 근사값 검증."""
        node = {
            "id": "x:1", "figmaId": "x:1", "name": "BG",
            "type": "FRAME",
            "fills": [
                {"type": "SOLID", "color": {"r": 0.05, "g": 0.05, "b": 0.07, "a": 1.0}}
            ],
        }
        result = normalize_tree(node)
        hex_color = result["fills"][0]["hexColor"]
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        assert r <= 20 and g <= 20 and b <= 25

    def test_opacity_preserved(self):
        node = {
            "id": "x:1", "figmaId": "x:1", "name": "Overlay",
            "type": "FRAME",
            "fills": [
                {"type": "SOLID", "color": {"r": 0.0, "g": 0.0, "b": 0.0, "a": 0.5}}
            ],
        }
        result = normalize_tree(node)
        assert result["fills"][0]["opacity"] == 0.5

    def test_no_fills_no_error(self):
        node = {"id": "x:1", "figmaId": "x:1", "name": "Empty", "type": "FRAME"}
        result = normalize_tree(node)
        assert result["id"] != "x:1"
        assert "fills" not in result


class TestNormalizeFill:
    def test_solid_fill_adds_hex(self):
        fill = {"type": "SOLID", "color": {"r": 1.0, "g": 0.0, "b": 0.0, "a": 1.0}}
        result = _normalize_fill(fill)
        assert result["hexColor"] == "#FF0000"
        assert result["opacity"] == 1.0

    def test_white_color(self):
        fill = {"type": "SOLID", "color": {"r": 1.0, "g": 1.0, "b": 1.0, "a": 1.0}}
        result = _normalize_fill(fill)
        assert result["hexColor"] == "#FFFFFF"

    def test_black_color(self):
        fill = {"type": "SOLID", "color": {"r": 0.0, "g": 0.0, "b": 0.0, "a": 1.0}}
        result = _normalize_fill(fill)
        assert result["hexColor"] == "#000000"

    def test_non_solid_fill_returns_unchanged(self):
        fill = {"type": "IMAGE", "imageRef": "abc123"}
        result = _normalize_fill(fill)
        assert "hexColor" not in result
        assert result["imageRef"] == "abc123"
