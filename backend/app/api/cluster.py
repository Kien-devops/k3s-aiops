import asyncio
from fastapi import APIRouter, Query
from typing import Optional
from app.core.context_builder import context_builder
from app.core.k8s_client import k8s_client
from app.datasources.prometheus import prom_client

router = APIRouter(prefix="/api/cluster", tags=["Cluster"])

@router.get("/status")
async def get_cluster_status():
    ctx = await context_builder.build_cluster_context()
    return {
        "health": ctx["health"],
        "power_watts": ctx["power_watts"],
        "pods_summary": ctx["pods_summary"],
        "anomaly_count": len(ctx["anomalies"])
    }

@router.get("/nodes")
async def get_nodes():
    nodes = await asyncio.to_thread(k8s_client.get_nodes)
    node_metrics = await prom_client.get_node_resource_metrics()
    return {
        "nodes": nodes,
        "metrics": node_metrics
    }

@router.get("/pods")
async def get_pods(namespace: Optional[str] = Query(None)):
    pods = await asyncio.to_thread(k8s_client.get_pods, namespace)
    return {
        "total": len(pods),
        "pods": pods
    }

@router.get("/anomalies")
async def get_anomalies():
    ctx = await context_builder.build_cluster_context()
    return {
        "total": len(ctx["anomalies"]),
        "anomalies": ctx["anomalies"]
    }

