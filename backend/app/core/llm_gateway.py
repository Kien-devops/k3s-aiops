import httpx
import logging
from typing import List, Dict, Any, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class LLMGateway:
    def __init__(self):
        self.base_url = settings.ROUTER_URL.rstrip("/")
        self.api_key = settings.ROUTER_KEY
        self.default_model = settings.ROUTER_MODEL

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.4,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Send chat completion request to 9Router LLM Gateway.
        """
        if not self.api_key:
            logger.error("ROUTER_KEY is not configured in environment.")
            return {
                "success": False,
                "error": "ROUTER_KEY is not configured. Please set ROUTER_KEY in secrets.",
                "content": "Lỗi cấu hình: Chưa thiết lập ROUTER_KEY trong Secret của cụm."
            }

        chosen_model = model or self.default_model
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "AIOps-Engine/2.0"
        }
        payload = {
            "model": chosen_model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        async with httpx.AsyncClient(verify=True, timeout=60.0) as client:
            try:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {})
                return {
                    "success": True,
                    "content": content,
                    "model": data.get("model", chosen_model),
                    "usage": usage
                }
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error from 9Router: {e.response.status_code} - {e.response.text}")
                return {
                    "success": False,
                    "error": f"9Router HTTP {e.response.status_code}: {e.response.text}",
                    "content": "Không thể kết nối đến AI Gateway (HTTP Error)."
                }
            except Exception as e:
                logger.error(f"Exception calling 9Router: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "content": f"Lỗi kết nối AI Gateway: {str(e)}"
                }

    async def test_connection(self) -> Dict[str, Any]:
        """Verify LLM Gateway connection and model availability."""
        if not self.api_key:
            return {
                "status": "unhealthy",
                "error": "ROUTER_KEY is not configured"
            }

        url = f"{self.base_url}/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "AIOps-Engine/2.0"
        }
        async with httpx.AsyncClient(verify=True, timeout=10.0) as client:
            try:
                resp = await client.get(url, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                models = [m.get("id") for m in data.get("data", [])]
                return {
                    "status": "healthy",
                    "available_models_count": len(models),
                    "active_model": self.default_model,
                    "has_target_model": self.default_model in models or any(self.default_model in m for m in models)
                }
            except Exception as e:
                return {
                    "status": "unhealthy",
                    "error": str(e)
                }

llm_gateway = LLMGateway()

