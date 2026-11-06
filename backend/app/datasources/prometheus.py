import httpx
import logging
from typing import Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)

class PrometheusClient:
    def __init__(self):
        self.base_url = settings.PROMETHEUS_URL.rstrip("/")

    async def query(self, query: str) -> List[Dict[str, Any]]:
        """Query instant PromQL vector."""
        url = f"{self.base_url}/api/v1/query"
        async with httpx.AsyncClient(timeout=6.0) as client:
            try:
                resp = await client.get(url, params={"query": query})
                resp.raise_for_status()
                data = resp.json()
                if data.get("status") == "success":
                    return data.get("data", {}).get("result", [])
                return []
            except Exception as e:
                logger.warning(f"Prometheus query failed '{query}': {e}")
                return []

    async def get_cluster_power_watts(self) -> float:
        """Total estimated wall power consumption in Watts."""
        results = await self.query("sum(node_power_estimated_wall_watts)")
        if results and len(results) > 0:
            try:
                return round(float(results[0]["value"][1]), 1)
            except (ValueError, IndexError):
                pass
        return 0.0

    async def get_node_resource_metrics(self) -> List[Dict[str, Any]]:
        """Fetch CPU and RAM usage percentage per node."""
        # 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100)
        cpu_query = '100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100)'
        # (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
        mem_query = '(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100'

        cpu_res = await self.query(cpu_query)
        mem_res = await self.query(mem_query)

        metrics_map = {}
        for item in cpu_res:
            instance = item.get("metric", {}).get("instance", "unknown")
            val = float(item["value"][1])
            metrics_map[instance] = {"instance": instance, "cpu_percent": round(val, 1), "mem_percent": 0.0}

        for item in mem_res:
            instance = item.get("metric", {}).get("instance", "unknown")
            val = float(item["value"][1])
            if instance in metrics_map:
                metrics_map[instance]["mem_percent"] = round(val, 1)
            else:
                metrics_map[instance] = {"instance": instance, "cpu_percent": 0.0, "mem_percent": round(val, 1)}

        return list(metrics_map.values())

    async def get_targets_status(self) -> Dict[str, Any]:
        """Check targets up/down state."""
        url = f"{self.base_url}/api/v1/targets"
        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json().get("data", {})
                active = data.get("activeTargets", [])
                up_count = sum(1 for t in active if t.get("health") == "up")
                return {
                    "total": len(active),
                    "up": up_count,
                    "down": len(active) - up_count,
                    "status": "healthy" if up_count > 0 else "degraded"
                }
            except Exception as e:
                return {"total": 0, "up": 0, "down": 0, "status": "unreachable", "error": str(e)}

prom_client = PrometheusClient()

