"""Optional local AI client supporting Ollama and local OpenAI-compatible endpoints."""
from typing import Optional
import json
import requests
from core.config import settings
from core.logging import get_logger

logger = get_logger("ai_client")


class LocalAIClient:
    """Manages communication with local Ollama inference server with graceful fallback."""

    def __init__(self, base_url: str = None, default_model: str = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = default_model or settings.OLLAMA_MODEL

    def is_available(self) -> tuple[bool, list[str]]:
        """
        Check if local Ollama server is running and list available models.
        Returns (is_available, model_names).
        """
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=2)
            if resp.status_code == 200:
                data = resp.json()
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                return True, models
            return False, []
        except Exception:
            return False, []

    def generate_completion(self, prompt: str, system_prompt: str = "") -> Optional[str]:
        """Send prompt to local Ollama model if available."""
        available, _ = self.is_available()
        if not available:
            return None

        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3
            }
        }

        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=30
            )
            if resp.status_code == 200:
                data = resp.json()
                return data.get("response", "").strip()
            return None
        except Exception as e:
            logger.warning(f"Local AI inference request failed: {e}")
            return None

    def enhance_outreach(
        self,
        company_name: str,
        category: str,
        service: str,
        observations: list[str],
        base_draft: str
    ) -> str:
        """
        Use local AI to polish an outreach message strictly preserving the evidence.
        Falls back to base_draft if model is offline.
        """
        system_prompt = (
            "You are a professional B2B outreach editor for XENITH Solutions. "
            "You MUST keep all factual observations and URLs exact. "
            "Never invent details or fabricate claims. Keep tone polite, consultative, and concise."
        )
        prompt = f"""Company: {company_name}
Category: {category}
Service Focus: {service}
Observable Evidence: {'; '.join(observations)}
Current Draft:
{base_draft}

Task: Polish the current draft for maximum clarity and engagement while maintaining 100% factual accuracy and keeping the opt-out notice at the bottom. Return only the revised message text."""

        response = self.generate_completion(prompt, system_prompt=system_prompt)
        return response if response else base_draft
