import pytest
from app.core.context_builder import ContextBuilder

def test_format_context_for_llm_contains_metrics_and_no_hardcoded_nodes():
    cb = ContextBuilder()
    mock_context = {
        "health": {"score": 85.0, "rating": "Bình thường (Good)"},
        "power_watts": 142.5,
        "nodes": [
            {"name": "server-tang2", "roles": ["control-plane"], "ready": True, "internal_ip": "100.98.92.34"},
            {"name": "server-tang4", "roles": ["worker"], "ready": True, "internal_ip": "100.72.138.65"}
        ],
        "pods_summary": {
            "total": 10,
            "running": 10,
            "terminating": 0,
            "abnormal_pods": []
        },
        "anomalies": [
            {
                "id": "high-cpu-tang4",
                "level": "WARNING",
                "title": "CPU cao trên server-tang4",
                "description": "CPU > 85%",
                "suggested_action": "Kiểm tra tải"
            }
        ],
        "recent_warning_events": [],
        "node_metrics": [
            {"instance": "server-tang4", "cpu_percent": 88.0, "mem_percent": 65.0}
        ],
        "recent_error_logs": [
            {"time": "2026-11-06T15:00:00Z", "app": "anhvan", "line": "Database connection timeout"}
        ]
    }
    
    formatted = cb.format_context_for_llm(mock_context)
    
    # Verify key sections
    assert "85.0/100" in formatted
    assert "142.5 Watts" in formatted
    assert "server-tang4: CPU 88.0%, RAM 65.0%" in formatted
    assert "Database connection timeout" in formatted
    assert "server-tang4" in formatted
    # Verify no arbitrary hardcoded node name is forced if not present
    assert "server-tang1" not in formatted
