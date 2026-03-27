"""figma_parser 단위 테스트"""
import pytest
from parsers.figma_parser import parse_figma_json, _parse_node
from core.exceptions import InvalidFigmaJsonException


class TestParseFigmaJson:
    def test_valid_json_returns_root_frame(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        assert result["name"] == "Landing Page"
        assert result["type"] == "FRAME"

    def test_missing_document_raises(self, figma_json_without_document):
        with pytest.raises(InvalidFigmaJsonException, match="'document'"):
            parse_figma_json(figma_json_without_document)

    def test_empty_canvas_raises(self, figma_json_empty_canvas):
        with pytest.raises(InvalidFigmaJsonException, match="FRAME"):
            parse_figma_json(figma_json_empty_canvas)

    def test_no_canvas_raises(self):
        figma_json = {
            "document": {"id": "0:0", "type": "DOCUMENT", "children": []}
        }
        with pytest.raises(InvalidFigmaJsonException, match="캔버스"):
            parse_figma_json(figma_json)

    def test_bounding_box_extracted(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        assert result["width"] == 1440
        assert result["height"] == 900

    def test_layout_mode_extracted(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        assert result["layoutMode"] == "VERTICAL"
        assert result["paddingTop"] == 80
        assert result["itemSpacing"] == 48

    def test_children_parsed_recursively(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        assert "children" in result
        child = result["children"][0]
        assert child["name"] == "HeroSection"
        assert "children" in child

    def test_text_node_characters_extracted(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        text_node = result["children"][0]["children"][0]
        assert text_node["type"] == "TEXT"
        assert text_node["characters"] == "AI로 디자인을 코드로"
        assert text_node["style"]["fontSize"] == 64

    def test_fills_preserved(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        assert "fills" in result
        assert result["fills"][0]["type"] == "SOLID"

    def test_corner_radius_extracted(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        hero = result["children"][0]
        assert hero["cornerRadius"] == 12

    def test_visible_defaults_to_true(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        assert result["visible"] is True

    def test_component_type_parsed(self):
        figma_json = {
            "document": {
                "id": "0:0", "type": "DOCUMENT",
                "children": [{
                    "id": "0:1", "type": "CANVAS",
                    "children": [{
                        "id": "1:1", "name": "MyComponent",
                        "type": "COMPONENT",
                        "absoluteBoundingBox": {"x": 0, "y": 0, "width": 400, "height": 300},
                        "children": [],
                    }],
                }],
            }
        }
        result = parse_figma_json(figma_json)
        assert result["type"] == "COMPONENT"

    def test_figma_id_preserved(self, minimal_figma_json):
        result = parse_figma_json(minimal_figma_json)
        assert result["figmaId"] == "1:1"


class TestParseNodeDepthLimit:
    def test_max_depth_truncates(self):
        """깊이 제한 초과 시 truncated 플래그 반환."""
        deep_node = {
            "id": "x:1", "name": "DeepNode", "type": "FRAME", "children": []
        }
        result = _parse_node(deep_node, depth=13, max_depth=12)
        assert result.get("truncated") is True

    def test_within_depth_not_truncated(self):
        node = {
            "id": "x:1", "name": "ShallowNode", "type": "FRAME",
            "absoluteBoundingBox": {"x": 0, "y": 0, "width": 100, "height": 100},
            "children": [],
        }
        result = _parse_node(node, depth=0)
        assert result.get("truncated") is not True
        assert result["name"] == "ShallowNode"
