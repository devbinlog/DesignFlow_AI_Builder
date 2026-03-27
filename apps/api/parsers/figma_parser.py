"""Figma JSON → 내부 노드 구조 변환기"""
from __future__ import annotations
from typing import Any
from core.exceptions import InvalidFigmaJsonException


SUPPORTED_NODE_TYPES = {
    "DOCUMENT", "CANVAS", "FRAME", "GROUP", "COMPONENT",
    "INSTANCE", "TEXT", "RECTANGLE", "ELLIPSE", "VECTOR",
    "BOOLEAN_OPERATION", "STAR", "LINE", "ARROW",
}

LAYOUT_MODES = {"NONE", "HORIZONTAL", "VERTICAL"}


def parse_figma_json(raw_json: dict[str, Any]) -> dict[str, Any]:
    """
    Figma raw JSON을 내부 파서 포맷으로 변환.
    최상위 document 노드부터 시작해 canvas → frame 순으로 탐색.
    """
    if "document" not in raw_json:
        raise InvalidFigmaJsonException("Figma JSON에 'document' 키가 없습니다.")

    document = raw_json["document"]
    canvases = document.get("children", [])

    if not canvases:
        raise InvalidFigmaJsonException("캔버스(페이지)가 없는 Figma 파일입니다.")

    # 첫 번째 캔버스의 최상위 프레임만 파싱 (랜딩 페이지 타입 대상)
    first_canvas = canvases[0]
    top_frames = [
        child for child in first_canvas.get("children", [])
        if child.get("type") in ("FRAME", "COMPONENT")
    ]

    if not top_frames:
        raise InvalidFigmaJsonException("캔버스에 파싱 가능한 FRAME이 없습니다.")

    # 첫 번째 최상위 프레임 파싱
    root_frame = top_frames[0]
    return _parse_node(root_frame, depth=0)


def _parse_node(node: dict[str, Any], depth: int, max_depth: int = 12) -> dict[str, Any]:
    """노드를 재귀적으로 파싱. 최대 깊이 제한."""
    if depth > max_depth:
        return {"id": node.get("id", ""), "name": node.get("name", ""), "type": node.get("type", ""), "truncated": True}

    node_type = node.get("type", "UNKNOWN")
    bbox = node.get("absoluteBoundingBox", {})

    parsed: dict[str, Any] = {
        "id": node.get("id", ""),
        "figmaId": node.get("id", ""),
        "name": node.get("name", ""),
        "type": node_type,
        "visible": node.get("visible", True),
    }

    # 바운딩 박스
    if bbox:
        parsed["width"] = bbox.get("width", 0)
        parsed["height"] = bbox.get("height", 0)
        parsed["x"] = bbox.get("x", 0)
        parsed["y"] = bbox.get("y", 0)

    # 레이아웃 속성 (Auto Layout)
    layout_mode = node.get("layoutMode", "NONE")
    if layout_mode in LAYOUT_MODES:
        parsed["layoutMode"] = layout_mode
        parsed["primaryAxisAlignItems"] = node.get("primaryAxisAlignItems", "MIN")
        parsed["counterAxisAlignItems"] = node.get("counterAxisAlignItems", "MIN")
        parsed["itemSpacing"] = node.get("itemSpacing", 0)
        parsed["paddingLeft"] = node.get("paddingLeft", 0)
        parsed["paddingRight"] = node.get("paddingRight", 0)
        parsed["paddingTop"] = node.get("paddingTop", 0)
        parsed["paddingBottom"] = node.get("paddingBottom", 0)

    # 시각 속성
    if "fills" in node:
        parsed["fills"] = node["fills"]
    if "strokes" in node:
        parsed["strokes"] = node["strokes"]
        parsed["strokeWeight"] = node.get("strokeWeight", 1)
    if "cornerRadius" in node:
        parsed["cornerRadius"] = node["cornerRadius"]

    # 텍스트 노드
    if node_type == "TEXT":
        parsed["characters"] = node.get("characters", "")
        parsed["style"] = node.get("style", {})

    # 자식 노드 재귀 파싱
    children = node.get("children", [])
    if children:
        parsed["children"] = [
            _parse_node(child, depth + 1, max_depth) for child in children
        ]

    return parsed
