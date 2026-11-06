import os
import re
import pytest
from app.config import settings
from app.core.llm_gateway import llm_gateway

def test_no_hardcoded_secret_in_config():
    """Ensure no hardcoded API key exists in config.py or default settings."""
    config_path = os.path.join(os.path.dirname(__file__), "..", "app", "config.py")
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Assert no sk-... key pattern is present in config.py
    assert not re.search(r'sk-[a-zA-Z0-9_\-]{15,}', content), "Found hardcoded API key in config.py!"

def test_no_disabled_tls_verification():
    """Ensure verify=False is not used in llm_gateway.py."""
    gateway_path = os.path.join(os.path.dirname(__file__), "..", "app", "core", "llm_gateway.py")
    with open(gateway_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "verify=False" not in content, "Found disabled TLS verification (verify=False) in llm_gateway.py!"

@pytest.mark.asyncio
async def test_llm_gateway_handles_missing_key_safely():
    """Ensure LLMGateway returns a clean error if key is empty rather than crashing."""
    original_key = llm_gateway.api_key
    try:
        llm_gateway.api_key = ""
        resp = await llm_gateway.chat([{"role": "user", "content": "hello"}])
        assert resp["success"] is False
        assert "ROUTER_KEY" in resp["error"]
    finally:
        llm_gateway.api_key = original_key

