from typing import Dict, Any, List

def calculate_cluster_health_score(
    nodes: List[Dict[str, Any]],
    pods: List[Dict[str, Any]],
    warning_events: List[Dict[str, Any]],
    power_watts: float = 0.0
) -> Dict[str, Any]:
    """
    Computes a comprehensive cluster health score from 0 to 100
    along with breakdown factors.
    """
    score = 100.0
    deductions = []

    # 1. Node Health Assessment
    total_nodes = len(nodes)
    if total_nodes > 0:
        ready_nodes = sum(1 for n in nodes if n.get("ready"))
        unready_nodes = total_nodes - ready_nodes
        if unready_nodes > 0:
            # -15 points per unready node
            node_penalty = min(35.0, unready_nodes * 15.0)
            score -= node_penalty
            deductions.append(f"{unready_nodes} node không sẵn sàng (NotReady): -{node_penalty:.0f}đ")

    # 2. Pod Health Assessment
    total_pods = len(pods)
    if total_pods > 0:
        terminating_pods = sum(1 for p in pods if p.get("status") == "Terminating")
        failed_pods = sum(1 for p in pods if p.get("status") in ["Failed", "CrashLoopBackOff", "Error"])
        unready_pods = sum(1 for p in pods if not p.get("is_ready") and p.get("status") != "Terminating")

        if terminating_pods > 0:
            pod_penalty = min(15.0, terminating_pods * 2.5)
            score -= pod_penalty
            deductions.append(f"{terminating_pods} pod đang bị kẹt Terminating: -{pod_penalty:.1f}đ")

        if failed_pods > 0:
            failed_penalty = min(25.0, failed_pods * 8.0)
            score -= failed_penalty
            deductions.append(f"{failed_pods} pod gặp lỗi/CrashLoop: -{failed_penalty:.1f}đ")

        if unready_pods > 0:
            unready_penalty = min(15.0, unready_pods * 3.0)
            score -= unready_penalty
            deductions.append(f"{unready_pods} pod chưa sẵn sàng: -{unready_penalty:.1f}đ")

    # 3. Warning Events Assessment
    if len(warning_events) > 0:
        event_penalty = min(15.0, len(warning_events) * 1.5)
        score -= event_penalty
        deductions.append(f"{len(warning_events)} sự kiện cảnh báo K8s gần đây: -{event_penalty:.1f}đ")

    # Clamp score
    final_score = max(0, min(100, round(score, 1)))

    if final_score >= 90:
        rating = "Tối ưu (Optimal)"
        badge_color = "emerald"
    elif final_score >= 75:
        rating = "Bình thường (Good)"
        badge_color = "blue"
    elif final_score >= 50:
        rating = "Xuống cấp (Degraded)"
        badge_color = "amber"
    else:
        rating = "Nguy cấp (Critical)"
        badge_color = "rose"

    return {
        "score": final_score,
        "rating": rating,
        "badge_color": badge_color,
        "deductions": deductions,
        "stats": {
            "total_nodes": total_nodes,
            "ready_nodes": sum(1 for n in nodes if n.get("ready")),
            "total_pods": total_pods,
            "running_pods": sum(1 for p in pods if p.get("status") == "Running" and p.get("is_ready")),
            "power_watts": power_watts
        }
    }

