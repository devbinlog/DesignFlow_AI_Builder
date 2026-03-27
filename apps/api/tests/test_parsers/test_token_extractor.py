"""token_extractor 단위 테스트"""
import pytest
from parsers.figma_parser import parse_figma_json
from parsers.normalizer import normalize_tree
from parsers.token_extractor import (
    extract_tokens,
    _px_to_tailwind_spacing,
    _px_to_tailwind_radius,
    _hex_brightness,
    _infer_color_name,
)


@pytest.fixture
def normalized_tree(minimal_figma_json):
    parsed = parse_figma_json(minimal_figma_json)
    return normalize_tree(parsed)


class TestExtractTokens:
    def test_returns_four_categories(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        assert set(result.keys()) == {"colors", "typography", "spacing", "radius"}

    def test_colors_extracted(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        assert len(result["colors"]) >= 1
        color = result["colors"][0]
        assert "id" in color
        assert "name" in color
        assert "value" in color
        assert color["value"].startswith("#")

    def test_typography_extracted(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        assert len(result["typography"]) >= 1
        typo = result["typography"][0]
        assert typo["fontFamily"] == "Inter"
        assert typo["fontSize"] == 64
        assert typo["fontWeight"] == 700

    def test_spacing_extracted(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        # paddingTop=80, paddingBottom=80, paddingLeft=120, paddingRight=120, itemSpacing=48
        spacing_values = [s["value"] for s in result["spacing"]]
        assert 80 in spacing_values
        assert 48 in spacing_values

    def test_radius_extracted(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        radius_values = [r["value"] for r in result["radius"]]
        assert 12 in radius_values

    def test_color_token_structure(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        color = result["colors"][0]
        assert "id" in color
        assert "cssVariable" in color
        assert "tailwindClass" in color
        assert "usageCount" in color
        assert color["usageCount"] >= 1

    def test_typography_tailwind_classes(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        typo = result["typography"][0]
        assert "tailwindClasses" in typo
        assert "text-" in typo["tailwindClasses"]

    def test_spacing_tailwind_class(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        sp = next((s for s in result["spacing"] if s["value"] == 48), None)
        assert sp is not None
        assert sp["tailwindClass"] == "12"

    def test_radius_tailwind_class(self, normalized_tree):
        result = extract_tokens(normalized_tree)
        r = next((r for r in result["radius"] if r["value"] == 12), None)
        assert r is not None
        assert r["tailwindClass"] == "rounded-xl"

    def test_empty_node_returns_empty_tokens(self):
        empty_node = {"id": "x:1", "figmaId": "x:1", "name": "Empty", "type": "FRAME"}
        result = extract_tokens(empty_node)
        assert result["colors"] == []
        assert result["typography"] == []
        assert result["spacing"] == []
        assert result["radius"] == []

    def test_usage_count_increments_for_same_color(self):
        """동일 색상 여러 번 사용 시 usageCount 증가 검증."""
        node = {
            "id": "x:1", "figmaId": "x:1", "name": "Parent",
            "type": "FRAME",
            "fills": [{"type": "SOLID", "hexColor": "#FF0000", "opacity": 1.0}],
            "children": [
                {
                    "id": "x:2", "figmaId": "x:2", "name": "Child1",
                    "type": "FRAME",
                    "fills": [{"type": "SOLID", "hexColor": "#FF0000", "opacity": 1.0}],
                },
                {
                    "id": "x:3", "figmaId": "x:3", "name": "Child2",
                    "type": "FRAME",
                    "fills": [{"type": "SOLID", "hexColor": "#FF0000", "opacity": 1.0}],
                },
            ],
        }
        result = extract_tokens(node)
        red_token = next((c for c in result["colors"] if c["value"] == "#FF0000"), None)
        assert red_token is not None
        assert red_token["usageCount"] == 3


class TestTailwindHelpers:
    @pytest.mark.parametrize("px,expected", [
        (4, "1"),
        (8, "2"),
        (16, "4"),
        (24, "6"),
        (48, "12"),
        (64, "16"),
        (999, "[999px]"),
    ])
    def test_px_to_tailwind_spacing(self, px, expected):
        assert _px_to_tailwind_spacing(px) == expected

    @pytest.mark.parametrize("px,expected", [
        (4, "rounded"),
        (6, "rounded-md"),
        (8, "rounded-lg"),
        (12, "rounded-xl"),
        (100, "rounded-full"),
        (50, "rounded-[50px]"),
    ])
    def test_px_to_tailwind_radius(self, px, expected):
        assert _px_to_tailwind_radius(px) == expected


class TestColorHelpers:
    def test_hex_brightness_black(self):
        assert _hex_brightness("#000000") < 5

    def test_hex_brightness_white(self):
        assert _hex_brightness("#FFFFFF") > 250

    def test_hex_brightness_invalid(self):
        result = _hex_brightness("invalid")
        assert result == 128

    def test_infer_color_name_dark(self):
        name = _infer_color_name("#0D0D12", 1.0, 0)
        assert "Background" in name

    def test_infer_color_name_overlay(self):
        name = _infer_color_name("#FFFFFF", 0.3, 0)
        assert "Overlay" in name

    def test_infer_color_name_light(self):
        name = _infer_color_name("#F2F2F5", 1.0, 0)
        assert "Text Light" in name or "Color" in name
