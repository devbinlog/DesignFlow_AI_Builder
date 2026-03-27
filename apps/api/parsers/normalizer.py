"""파싱된 노드 트리를 정규화"""
from __future__ import annotations
from typing import Any
import uuid


def normalize_tree(parsed_node: dict[str, Any]) -> dict[str, Any]:
    """
    파싱된 Figma 노드 트리에 내부 UUID를 부여하고 정규화.
    """
    return _normalize_node(parsed_node)


def _normalize_node(node: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(node)

    # 내부 UUID 부여 (Figma ID와 별개)
    normalized["id"] = str(uuid.uuid4())
    normalized["figmaId"] = node.get("figmaId", node.get("id", ""))

    # fills에서 색상값 정규화
    if "fills" in normalized:
        normalized["fills"] = [_normalize_fill(f) for f in normalized["fills"]]

    # 자식 재귀 정규화
    if "children" in normalized:
        normalized["children"] = [_normalize_node(child) for child in normalized["children"]]

    return normalized


def _normalize_fill(fill: dict[str, Any]) -> dict[str, Any]:
    """fill 색상을 hex 값으로 정규화"""
    normalized = dict(fill)
    if fill.get("type") == "SOLID" and "color" in fill:
        color = fill["color"]
        r = int(color.get("r", 0) * 255)
        g = int(color.get("g", 0) * 255)
        b = int(color.get("b", 0) * 255)
        a = color.get("a", 1.0)
        normalized["hexColor"] = f"#{r:02X}{g:02X}{b:02X}"
        normalized["opacity"] = a
    return normalized
