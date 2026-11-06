from fastapi import APIRouter
from app.core.llm_gateway import llm_gateway
from app.core.k8s_client import k8s_client
from app.datasources.prometheus import prom_client
from app.datasources.loki import loki_client
from app.datasources.tempo import tempo_client
from app.config import settings

router = APIRouter(prefix="/api/health", tags=["Health"])

@router.get("")
async def get_health():
    """Fast probe endpoint for Kubernetes liveness/readiness probes."""
    return {"status": "ok", "service": settings.APP_NAME}

@router.get("/details")
async def get_health_details():
    """Detailed health check for all upstream observability and AI integrations."""
    llm_status = await llm_gateway.test_connection()
    prom_status = await prom_client.get_targets_status()
    loki_ready = await loki_client.check_health()
    tempo_ready = await tempo_client.check_health()

    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "components": {
            "llm_gateway": {
                "endpoint": settings.ROUTER_URL,
                "model": settings.ROUTER_MODEL,
                **llm_status
            },
            "k8s_api": {
                "connected": k8s_client.initialized,
                "node_count": len(k8s_client.get_nodes()) if k8s_client.initialized else 0
            },
            "prometheus": {
                "endpoint": settings.PROMETHEUS_URL,
                **prom_status
            },
            "loki": {
                "endpoint": settings.LOKI_URL,
                "ready": loki_ready
            },
            "tempo": {
                "endpoint": settings.TEMPO_URL,
                "ready": tempo_ready
            }
        }
    }

