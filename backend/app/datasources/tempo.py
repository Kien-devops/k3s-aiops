import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class TempoClient:
    def __init__(self):
        self.base_url = settings.TEMPO_URL.rstrip("/")

    async def check_health(self) -> bool:
        url = f"{self.base_url}/ready"
        async with httpx.AsyncClient(timeout=3.0) as client:
            try:
                resp = await client.get(url)
                return resp.status_code == 200
            except Exception:
                return False

tempo_client = TempoClient()

