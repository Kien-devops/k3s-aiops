import json
from typing import Dict, Any
from app.core.k8s_client import k8s_client
from app.datasources.prometheus import prom_client
from app.datasources.loki import loki_client
from app.analytics.health_score import calculate_cluster_health_score
from app.analytics.anomaly_detector import detect_cluster_anomalies

class ContextBuilder:
    async def build_cluster_context(self) -> Dict[str, Any]:
        """
        Gathers live state from K3s API, Prometheus, and Loki.
        """
        nodes = k8s_client.get_nodes()
        pods = k8s_client.get_pods()
        events = k8s_client.get_recent_warning_events(limit=10)
        power_watts = await prom_client.get_cluster_power_watts()
        node_metrics = await prom_client.get_node_resource_metrics()
        loki_logs = await loki_client.query_logs(limit=10)

        health_data = calculate_cluster_health_score(nodes, pods, events, power_watts)
        anomalies = detect_cluster_anomalies(nodes, pods, events, power_watts, node_metrics)

        return {
            "health": health_data,
            "anomalies": anomalies,
            "nodes": nodes,
            "pods_summary": {
                "total": len(pods),
                "running": sum(1 for p in pods if p.get("status") == "Running" and p.get("is_ready")),
                "terminating": sum(1 for p in pods if p.get("status") == "Terminating"),
                "abnormal_pods": [p for p in pods if not p.get("is_ready") or p.get("status") != "Running"]
            },
            "recent_warning_events": events,
            "power_watts": power_watts,
            "node_metrics": node_metrics,
            "recent_error_logs": loki_logs
        }

    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """
        Formats JSON context into a clean markdown summary for GPT-5.6-sol.
        """
        health = context["health"]
        nodes = context["nodes"]
        pods_sum = context["pods_summary"]
        anomalies = context["anomalies"]
        events = context["recent_warning_events"]
        power = context["power_watts"]

        node_str = "\n".join([f"- {n['name']} ({n.get('roles', ['worker'])}): {'READY' if n.get('ready') else 'NOT READY'} | IP: {n.get('internal_ip')}" for n in nodes])
        
        abnormal_str = "None"
        if pods_sum["abnormal_pods"]:
            abnormal_str = "\n".join([f"- Pod: {p['name']} (Namespace: {p['namespace']}) | Status: {p['status']} | Node: {p.get('node')} | Restarts: {p.get('restarts')}" for p in pods_sum["abnormal_pods"][:10]])

        anomalies_str = "None"
        if anomalies:
            anomalies_str = "\n".join([f"- [{a['level']}] {a['title']}: {a['description']} (Action: {a['suggested_action']})" for a in anomalies])

        events_str = "None"
        if events:
            events_str = "\n".join([f"- [{e['time']}] {e['namespace']}/{e['object']}: {e['reason']} - {e['message']}" for e in events[:5]])

        node_metrics = context.get("node_metrics", [])
        metrics_str = "None"
        if node_metrics:
            metrics_str = "\n".join([f"- {m['instance']}: CPU {m.get('cpu_percent', 0):.1f}%, RAM {m.get('mem_percent', 0):.1f}%" for m in node_metrics])

        error_logs = context.get("recent_error_logs", [])
        logs_str = "None"
        if error_logs:
            logs_str = "\n".join([f"- [{l.get('time', 'unknown')}] ({l.get('app', 'app')}): {l.get('line', '')[:200]}" for l in error_logs[:5]])

        return f"""### LIVE K3S CLUSTER TELEMETRY CONTEXT:
* **Cluster Health Score**: {health['score']}/100 ({health['rating']})
* **Estimated Wall Power**: {power} Watts
* **Nodes**:
{node_str}
* **Node CPU/RAM Metrics**:
{metrics_str}
* **Pods Status**: {pods_sum['running']}/{pods_sum['total']} Running, {pods_sum['terminating']} Terminating
* **Abnormal / Stuck Pods**:
{abnormal_str}
* **Detected Operational Anomalies**:
{anomalies_str}
* **Recent K8s Warning Events**:
{events_str}
* **Recent Application Error Logs (Loki)**:
{logs_str}
"""

context_builder = ContextBuilder()

