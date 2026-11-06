import httpx
import logging
from typing import List, Dict, Any
from app.config import settings

logger = logging.getLogger(__name__)

class LokiClient:
    def __init__(self):
        self.base_url = settings.LOKI_URL.rstrip("/")

    async def query_logs(self, query: str = '{namespace=~".+"} |= "error"', limit: int = 20) -> List[Dict[str, Any]]:
        """Query log entries from Loki."""
        url = f"{self.base_url}/loki/api/v1/query_range"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(url, params={"query": query, "limit": limit})
                resp.raise_for_status()
                data = resp.json().get("data", {}).get("result", [])
                logs = []
                for stream in data:
                    labels = stream.get("stream", {})
                    for entry in stream.get("values", []):
                        logs.append({
                            "timestamp": entry[0],
                            "message": entry[1],
                            "labels": labels
                        })
                return logs
            except Exception as e:
                logger.debug(f"Loki query note (Loki might not have data yet): {e}")
                return []

    async def check_health(self) -> bool:
        url = f"{self.base_url}/ready"
        async with httpx.AsyncClient(timeout=3.0) as client:
            try:
                resp = await client.get(url)
                return resp.status_code == 200
            except Exception:
                return False

loki_client = LokiClient()

