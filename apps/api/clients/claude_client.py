"""AI 클라이언트 — Ollama (로컬) 또는 Anthropic API 자동 선택"""
from __future__ import annotations
import json
import logging
from pathlib import Path
import httpx
from core.config import settings
from core.exceptions import AIServiceException

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent.parent / "prompts"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"


def _load_prompt(filename: str) -> str:
    prompt_path = PROMPTS_DIR / filename
    if prompt_path.exists():
        content = prompt_path.read_text(encoding="utf-8")
        lines = content.split("\n")
        in_block = False
        prompt_lines = []
        for line in lines:
            if line.strip() == "```" and in_block:
                in_block = False
            elif in_block:
                prompt_lines.append(line)
            elif line.strip().startswith("```") and not in_block:
                in_block = True
        if prompt_lines:
            return "\n".join(prompt_lines)
    return "You are an expert frontend architect. Respond only with valid JSON."


def _strip_json_fence(text: str) -> str:
    """마크다운 코드 블록 제거."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # 첫 줄(```json 또는 ```) 과 마지막 줄(```) 제거
        inner = lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        text = "\n".join(inner).strip()
    return text


class ClaudeClient:
    """Ollama 우선, 없으면 Anthropic API로 폴백하는 통합 AI 클라이언트."""

    async def call(self, system_prompt: str, user_message: str) -> dict:
        # Ollama 서버가 살아있으면 Ollama 사용
        if await self._ollama_available():
            return await self._call_ollama(system_prompt, user_message)
        # Anthropic API 키가 설정되어 있으면 Claude 사용
        if settings.anthropic_api_key and settings.anthropic_api_key != "your-api-key-here":
            return await self._call_anthropic(system_prompt, user_message)
        raise AIServiceException("사용 가능한 AI 백엔드가 없습니다. Ollama를 실행하거나 ANTHROPIC_API_KEY를 설정하세요.")

    async def _ollama_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                return r.status_code == 200
        except Exception:
            return False

    async def _call_ollama(self, system_prompt: str, user_message: str) -> dict:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "stream": False,
            "options": {"temperature": 0.1},
        }
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
                response.raise_for_status()
                data = response.json()
                raw_text = data["message"]["content"]
                logger.info("Ollama 응답 수신 (model=%s, %d chars)", OLLAMA_MODEL, len(raw_text))
                return json.loads(_strip_json_fence(raw_text))
        except json.JSONDecodeError as e:
            logger.error("Ollama 응답 JSON 파싱 실패: %s", e)
            raise AIServiceException(f"AI 응답을 JSON으로 파싱할 수 없습니다: {e}")
        except httpx.HTTPError as e:
            logger.error("Ollama 호출 오류: %s", e)
            raise AIServiceException(f"Ollama 호출 실패: {e}")

    async def _call_anthropic(self, system_prompt: str, user_message: str) -> dict:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
            response = client.messages.create(
                model=settings.ai_model,
                max_tokens=settings.ai_max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            raw_text = response.content[0].text
            logger.info("Anthropic 응답 수신 (model=%s)", settings.ai_model)
            return json.loads(_strip_json_fence(raw_text))
        except json.JSONDecodeError as e:
            logger.error("Anthropic 응답 JSON 파싱 실패: %s", e)
            raise AIServiceException(f"AI 응답을 JSON으로 파싱할 수 없습니다: {e}")
        except Exception as e:
            logger.error("Anthropic API 오류: %s", e)
            raise AIServiceException(f"AI API 호출 실패: {e}")

    def get_analysis_prompt(self) -> str:
        return _load_prompt("system_prompt_analysis.md")

    def get_naming_prompt(self) -> str:
        return _load_prompt("system_prompt_naming.md")

    def get_codegen_prompt(self) -> str:
        return _load_prompt("system_prompt_codegen.md")


claude_client = ClaudeClient()
