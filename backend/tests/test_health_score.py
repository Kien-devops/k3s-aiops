import pytest
from app.analytics.health_score import calculate_cluster_health_score

def test_perfect_cluster_health():
    nodes = [{"name": "node-1", "ready": True}, {"name": "node-2", "ready": True}]
    pods = [{"name": "app-1", "status": "Running", "is_ready": True, "restarts": 0}]
    events = []
    
    result = calculate_cluster_health_score(nodes, pods, events, power_watts=120.0)
    assert result["score"] == 100.0
    assert result["rating"] == "Tối ưu (Optimal)"
    assert len(result["deductions"]) == 0

def test_unready_node_penalty():
    nodes = [{"name": "node-1", "ready": True}, {"name": "node-2", "ready": False}]
    pods = [{"name": "app-1", "status": "Running", "is_ready": True, "restarts": 0}]
    events = []
    
    result = calculate_cluster_health_score(nodes, pods, events, power_watts=100.0)
    assert result["score"] == 85.0
    assert any("node không sẵn sàng" in d for d in result["deductions"])

def test_failed_and_terminating_pods():
    nodes = [{"name": "node-1", "ready": True}]
    pods = [
        {"name": "p-1", "status": "Terminating", "is_ready": False, "restarts": 0},
        {"name": "p-2", "status": "CrashLoopBackOff", "is_ready": False, "restarts": 5}
    ]
    events = [{"reason": "BackOff", "message": "Back-off restarting failed container"}]
    
    result = calculate_cluster_health_score(nodes, pods, events, power_watts=110.0)
    assert result["score"] < 90.0
    assert result["stats"]["total_pods"] == 2

def test_score_clamping_at_zero():
    nodes = [{"name": f"node-{i}", "ready": False} for i in range(10)]
    pods = [{"name": f"pod-{i}", "status": "CrashLoopBackOff", "is_ready": False} for i in range(20)]
    events = [{"reason": "Failed"} for _ in range(50)]
    
    result = calculate_cluster_health_score(nodes, pods, events, power_watts=500.0)
    assert result["score"] >= 0.0
    assert result["rating"] == "Nguy cấp (Critical)"

