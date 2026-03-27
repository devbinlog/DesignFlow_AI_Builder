"""정규화된 노드 트리에서 디자인 토큰 추출"""
from __future__ import annotations
from typing import Any
import uuid


def extract_tokens(normalized_tree: dict[str, Any]) -> dict[str, Any]:
    """
    노드 트리를 순회하며 색상, 타이포그래피, 간격, 반경 토큰 추출.
    """
    state: dict[str, Any] = {
        "colors": {},
        "typography": {},
        "spacing": set(),
        "radius": set(),
    }

    _traverse(normalized_tree, state)

    return {
        "colors": _build_color_tokens(state["colors"]),
        "typography": _build_typography_tokens(state["typography"]),
        "spacing": _build_spacing_tokens(state["spacing"]),
        "radius": _build_radius_tokens(state["radius"]),
    }


def _traverse(node: dict[str, Any], state: dict[str, Any]) -> None:
    # 색상 추출 (fills)
    for fill in node.get("fills", []):
        if fill.get("type") == "SOLID" and "hexColor" in fill:
            hex_val = fill["hexColor"]
            opacity = fill.get("opacity", 1.0)
            key = f"{hex_val}_{opacity:.2f}"
            if key not in state["colors"]:
                state["colors"][key] = {
                    "value": hex_val,
                    "opacity": opacity,
                    "usageCount": 0,
                    "usageNodes": [],
                }
            state["colors"][key]["usageCount"] += 1
            state["colors"][key]["usageNodes"].append(node.get("figmaId", ""))

    # 타이포그래피 추출
    if node.get("type") == "TEXT" and "style" in node:
        style = node["style"]
        key = f"{style.get('fontFamily','')}_{style.get('fontSize',0)}_{style.get('fontWeight',400)}"
        if key not in state["typography"]:
            state["typography"][key] = {
                "fontFamily": style.get("fontFamily", "Inter"),
                "fontSize": style.get("fontSize", 14),
                "fontWeight": style.get("fontWeight", 400),
                "lineHeight": style.get("lineHeightPx", style.get("fontSize", 14) * 1.5),
                "letterSpacing": style.get("letterSpacing", 0),
                "usageNodes": [],
            }
        state["typography"][key]["usageNodes"].append(node.get("figmaId", ""))

    # 간격 추출 (padding, itemSpacing)
    for spacing_key in ("paddingLeft", "paddingRight", "paddingTop", "paddingBottom", "itemSpacing"):
        val = node.get(spacing_key, 0)
        if val and val > 0:
            state["spacing"].add(val)

    # 반경 추출
    radius = node.get("cornerRadius", 0)
    if radius and radius > 0:
        state["radius"].add(radius)

    # 자식 재귀 순회
    for child in node.get("children", []):
        _traverse(child, state)


def _px_to_tailwind_spacing(px: int) -> str:
    tailwind_map = {
        1: "px", 2: "0.5", 4: "1", 6: "1.5", 8: "2", 10: "2.5",
        12: "3", 14: "3.5", 16: "4", 20: "5", 24: "6", 28: "7",
        32: "8", 36: "9", 40: "10", 48: "12", 56: "14", 64: "16",
        80: "20", 96: "24", 112: "28", 120: "30", 128: "32",
    }
    return tailwind_map.get(px, f"[{px}px]")


def _px_to_tailwind_radius(px: int) -> str:
    radius_map = {
        2: "rounded-sm", 4: "rounded", 6: "rounded-md",
        8: "rounded-lg", 12: "rounded-xl", 16: "rounded-2xl",
        24: "rounded-3xl", 100: "rounded-full",
    }
    return radius_map.get(px, f"rounded-[{px}px]")


def _infer_color_name(hex_val: str, opacity: float, index: int) -> str:
    """간단한 색상 이름 추론 (AI가 나중에 재명명)"""
    brightness = _hex_brightness(hex_val)
    if brightness < 30:
        return f"Background {index+1}"
    elif brightness < 80:
        return f"Surface {index+1}"
    elif brightness > 200:
        return f"Text Light {index+1}"
    elif opacity < 0.5:
        return f"Overlay {index+1}"
    else:
        return f"Color {index+1}"


def _hex_brightness(hex_val: str) -> int:
    try:
        r = int(hex_val[1:3], 16)
        g = int(hex_val[3:5], 16)
        b = int(hex_val[5:7], 16)
        return int(0.299 * r + 0.587 * g + 0.114 * b)
    except (ValueError, IndexError):
        return 128


def _build_color_tokens(colors: dict) -> list[dict]:
    tokens = []
    for i, (key, data) in enumerate(colors.items()):
        token: dict[str, Any] = {
            "id": f"color-{i+1}",
            "name": _infer_color_name(data["value"], data["opacity"], i),
            "value": data["value"],
            "opacity": data["opacity"],
            "usageCount": data["usageCount"],
            "cssVariable": f"--color-{i+1}",
            "tailwindClass": f"bg-[{data['value']}]",
            "usageNodes": data["usageNodes"][:5],
        }
        tokens.append(token)
    return tokens


def _build_typography_tokens(typography: dict) -> list[dict]:
    tokens = []
    for i, (key, data) in enumerate(typography.items()):
        size = data["fontSize"]
        weight = data["fontWeight"]

        if size >= 48 and weight >= 700:
            name = "Display / Extra Bold"
        elif size >= 32 and weight >= 700:
            name = "Heading 1 / Bold"
        elif size >= 24:
            name = f"Heading 2 / {_weight_name(weight)}"
        elif size >= 18:
            name = f"Heading 3 / {_weight_name(weight)}"
        elif size >= 16:
            name = f"Body Large / {_weight_name(weight)}"
        elif size >= 14:
            name = f"Body / {_weight_name(weight)}"
        else:
            name = f"Caption / {_weight_name(weight)}"

        tokens.append({
            "id": f"type-{i+1}",
            "name": name,
            "fontFamily": data["fontFamily"],
            "fontSize": size,
            "fontWeight": weight,
            "lineHeight": data["lineHeight"],
            "letterSpacing": data["letterSpacing"],
            "tailwindClasses": _build_tailwind_typography(size, weight, data["lineHeight"]),
            "usageNodes": data["usageNodes"][:5],
        })
    return tokens


def _weight_name(weight: int) -> str:
    weight_map = {100: "Thin", 200: "ExtraLight", 300: "Light", 400: "Regular",
                  500: "Medium", 600: "Semibold", 700: "Bold", 800: "ExtraBold", 900: "Black"}
    return weight_map.get(weight, "Regular")


def _build_tailwind_typography(size: int, weight: int, line_height: float) -> str:
    size_map = {12: "text-xs", 13: "text-[13px]", 14: "text-sm", 15: "text-[15px]",
                16: "text-base", 18: "text-lg", 20: "text-xl", 24: "text-2xl",
                28: "text-[28px]", 32: "text-3xl", 36: "text-4xl", 40: "text-[40px]",
                48: "text-5xl", 56: "text-[56px]", 64: "text-6xl", 72: "text-7xl"}
    weight_map = {400: "font-normal", 500: "font-medium", 600: "font-semibold",
                  700: "font-bold", 800: "font-extrabold", 900: "font-black"}

    parts = [
        size_map.get(size, f"text-[{size}px]"),
        weight_map.get(weight, f"font-[{weight}]"),
    ]
    return " ".join(parts)


def _build_spacing_tokens(spacing: set) -> list[dict]:
    tokens = []
    for i, val in enumerate(sorted(spacing)):
        tokens.append({
            "id": f"sp-{i+1}",
            "value": int(val),
            "tailwindClass": _px_to_tailwind_spacing(int(val)),
            "usageContext": "padding/gap",
        })
    return tokens


def _build_radius_tokens(radius: set) -> list[dict]:
    tokens = []
    for i, val in enumerate(sorted(radius)):
        tokens.append({
            "id": f"r-{i+1}",
            "value": int(val),
            "tailwindClass": _px_to_tailwind_radius(int(val)),
        })
    return tokens
