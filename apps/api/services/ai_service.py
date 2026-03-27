"""AI 해석 서비스 — Claude API 호출 및 결과 처리"""
from __future__ import annotations
import json
import logging
from typing import Any
from clients.claude_client import claude_client
from core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


async def analyze_structure(normalized_tree: dict[str, Any], design_tokens: dict[str, Any]) -> dict[str, Any]:
    """Step 1: 노드 구조 분석"""
    system = claude_client.get_analysis_prompt()
    user = f"다음 Figma 노드 구조와 디자인 토큰을 분석하세요:\n\n## 노드 트리\n{json.dumps(normalized_tree, ensure_ascii=False, indent=2)}\n\n## 디자인 토큰\n{json.dumps(design_tokens, ensure_ascii=False, indent=2)}"
    try:
        return await _safe_call(system, user)
    except AIServiceException:
        logger.warning("분석 AI 호출 실패 — 기본 구조 반환")
        return _fallback_analysis(normalized_tree)


async def name_components(component_candidates: list[dict]) -> dict[str, Any]:
    """Step 2: 컴포넌트 명명"""
    system = claude_client.get_naming_prompt()
    user = f"다음 컴포넌트 후보들에 이름을 제안하세요:\n\n{json.dumps(component_candidates, ensure_ascii=False, indent=2)}"
    try:
        result = await _safe_call(system, user)
        # namedComponents를 candidates에 병합
        named_map = {n["nodeId"]: n for n in result.get("namedComponents", [])}
        for candidate in component_candidates:
            if candidate["nodeId"] in named_map:
                named = named_map[candidate["nodeId"]]
                candidate["suggestedName"] = named.get("suggestedName", candidate.get("figmaName", "Component"))
                candidate["filePath"] = named.get("filePath", "")
        return {"componentCandidates": component_candidates}
    except AIServiceException:
        logger.warning("명명 AI 호출 실패 — figmaName 사용")
        for c in component_candidates:
            if not c.get("suggestedName"):
                c["suggestedName"] = _pascal_case(c.get("figmaName", "Component"))
        return {"componentCandidates": component_candidates}


async def generate_code(component_candidates: list[dict], design_tokens: dict[str, Any]) -> dict[str, Any]:
    """Step 3: 코드 생성"""
    system = claude_client.get_codegen_prompt()
    user = (
        f"다음 컴포넌트 구조와 디자인 토큰을 기반으로 React + Tailwind 코드를 생성하세요:\n\n"
        f"## 컴포넌트 구조\n{json.dumps(component_candidates, ensure_ascii=False, indent=2)}\n\n"
        f"## 디자인 토큰\n{json.dumps(design_tokens, ensure_ascii=False, indent=2)}"
    )
    try:
        return await _safe_call(system, user)
    except AIServiceException:
        logger.warning("코드 생성 AI 호출 실패 — 기본 코드 반환")
        return _fallback_codegen(component_candidates)


async def _safe_call(system: str, user: str) -> dict:
    return await claude_client.call(system, user)


def _fallback_analysis(tree: dict[str, Any]) -> dict[str, Any]:
    return {
        "componentCandidates": [
            {
                "nodeId": tree.get("id", "root"),
                "figmaName": tree.get("name", "Root"),
                "suggestedName": _pascal_case(tree.get("name", "Root")),
                "componentType": "section",
                "isRepeating": False,
                "confidence": 0.5,
                "reasoning": "AI 분석 실패로 인한 기본값",
                "children": [],
            }
        ],
        "layoutPattern": "unknown",
        "topLevelSections": [],
        "warnings": [{"type": "LOW_CONFIDENCE", "nodeId": tree.get("id", "root"), "message": "AI 분석에 실패했습니다. 수동 확인이 필요합니다."}],
    }


def _fallback_codegen(candidates: list[dict]) -> dict[str, Any]:
    files = []
    for c in candidates:
        name = c.get("suggestedName", "Component")
        files.append({
            "path": f"components/{name}.tsx",
            "type": "section",
            "content": f'export function {name}() {{\n  return <div>{name}</div>\n}}\n',
        })
    files.append({
        "path": "app/page.tsx",
        "type": "page",
        "content": "export default function Page() {\n  return <main />\n}\n",
    })
    return {"files": files}


def _pascal_case(name: str) -> str:
    return "".join(word.capitalize() for word in name.replace("-", " ").replace("_", " ").split())
