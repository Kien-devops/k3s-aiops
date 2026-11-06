import pytest
from app.analytics.anomaly_detector import detect_cluster_anomalies

def test_detect_unready_node():
    nodes = [{"name": "server-tang1", "ready": False, "internal_ip": "100.67.248.86"}]
    pods = []
    events = []
    
    anomalies = detect_cluster_anomalies(nodes, pods, events)
    assert len(anomalies) == 1
    assert anomalies[0]["level"] == "CRITICAL"
    assert "server-tang1" in anomalies[0]["title"]

def test_detect_stuck_terminating_pods():
    nodes = [{"name": "server-tang1", "ready": False}]
    pods = [
        {"name": "app-x", "namespace": "default", "status": "Terminating", "node": "server-tang1"},
        {"name": "app-y", "namespace": "default", "status": "Terminating", "node": "server-tang1"}
    ]
    events = []
    
    anomalies = detect_cluster_anomalies(nodes, pods, events)
    stuck_anomaly = [a for a in anomalies if a["category"] == "Workloads"]
    assert len(stuck_anomaly) == 1
    assert "2 pod bị kẹt Terminating" in stuck_anomaly[0]["title"]

def test_detect_high_resource_thresholds():
    nodes = [{"name": "server-tang4", "ready": True}]
    pods = []
    events = []
    metrics = [
        {"instance": "server-tang4", "cpu_percent": 92.5, "mem_percent": 94.0}
    ]
    
    anomalies = detect_cluster_anomalies(nodes, pods, events, power_watts=280.0, node_metrics=metrics)
    categories = [a["category"] for a in anomalies]
    assert "Resource" in categories
    assert "Energy" in categories

