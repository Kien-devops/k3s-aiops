from typing import List, Dict, Any

def detect_cluster_anomalies(
    nodes: List[Dict[str, Any]],
    pods: List[Dict[str, Any]],
    warning_events: List[Dict[str, Any]],
    power_watts: float = 0.0,
    node_metrics: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Detect actionable operational anomalies across cluster infrastructure.
    """
    anomalies = []

    # 1. Check for unready nodes
    for n in nodes:
        if not n.get("ready"):
            anomalies.append({
                "id": f"node-unready-{n['name']}",
                "level": "CRITICAL",
                "category": "Infrastructure",
                "title": f"Node {n['name']} đang ở trạng thái NotReady",
                "description": f"Node {n['name']} ({n.get('internal_ip', 'unknown')}) mất liên lạc với control plane. Cần kiểm tra nguồn điện hoặc mạng.",
                "suggested_action": f"Kiểm tra kết nối mạng/nguồn máy chủ hoặc chạy: kubectl describe node {n['name']}"
            })

    # 2. Check for terminating/stuck pods
    terminating_by_node = {}
    for p in pods:
        if p.get("status") == "Terminating":
            node = p.get("node") or "unknown"
            terminating_by_node.setdefault(node, []).append(p)

    for node, stuck_pods in terminating_by_node.items():
        anomalies.append({
            "id": f"pods-terminating-{node}",
            "level": "WARNING",
            "category": "Workloads",
            "title": f"Có {len(stuck_pods)} pod bị kẹt Terminating trên node {node}",
            "description": f"Các pod thuộc namespace: {', '.join(set(p['namespace'] for p in stuck_pods))} không thể giải phóng do node đích không phản hồi.",
            "suggested_action": f"Force delete pods nếu node đã ngừng hoạt động: kubectl delete pod --force --grace-period=0 -n <ns> <pod>"
        })

    # 3. Check for pods with high restart counts
    for p in pods:
        if p.get("restarts", 0) > 5:
            anomalies.append({
                "id": f"pod-restarts-{p['name']}",
                "level": "WARNING",
                "category": "Application",
                "title": f"Pod {p['name']} đã restart {p['restarts']} lần",
                "description": f"Pod {p['name']} tại namespace {p['namespace']} bị restart nhiều lần, có thể do CrashLoopBackOff hoặc OOMKilled.",
                "suggested_action": f"Xem log chi tiết: kubectl logs -n {p['namespace']} {p['name']} --previous"
            })

    # 4. Check for high CPU or Memory on nodes
    if node_metrics:
        for m in node_metrics:
            if m.get("cpu_percent", 0) > 85.0:
                anomalies.append({
                    "id": f"high-cpu-{m['instance']}",
                    "level": "WARNING",
                    "category": "Resource",
                    "title": f"CPU cao trên {m['instance']} ({m['cpu_percent']}%)",
                    "description": "Mức sử dụng CPU vượt ngưỡng cảnh báo 85%.",
                    "suggested_action": "Kiểm tra các tiến trình tốn tài nguyên hoặc scale thêm replica."
                })
            if m.get("mem_percent", 0) > 90.0:
                anomalies.append({
                    "id": f"high-mem-{m['instance']}",
                    "level": "CRITICAL",
                    "category": "Resource",
                    "title": f"Bộ nhớ RAM quá tải trên {m['instance']} ({m['mem_percent']}%)",
                    "description": "Mức sử dụng RAM vượt ngưỡng nguy cấp 90%, nguy cơ OOM killer xuất hiện.",
                    "suggested_action": "Kiểm tra memory leaks hoặc bổ sung node compute."
                })

    # 5. Check cluster total power threshold
    if power_watts > 250.0:
        anomalies.append({
            "id": "high-cluster-power",
            "level": "INFO",
            "category": "Energy",
            "title": f"Công suất tiêu thụ cao: {power_watts} W",
            "description": f"Tổng công suất cluster đang tiêu thụ {power_watts} W, vượt mức trung bình idle (~140W).",
            "suggested_action": "Kiểm tra các tác vụ đang load trên các server Xeon."
        })

    return anomalies

