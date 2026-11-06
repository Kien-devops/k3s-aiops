import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # LLM Gateway
    ROUTER_URL: str = os.getenv("ROUTER_URL", "https://9router.onprem.site/v1")
    ROUTER_KEY: str = os.getenv("ROUTER_KEY", "")
    ROUTER_MODEL: str = os.getenv("ROUTER_MODEL", "gpt-5.6-sol")

    # Observability Data Sources
    PROMETHEUS_URL: str = os.getenv("PROMETHEUS_URL", "http://100.112.150.56:9090")
    LOKI_URL: str = os.getenv("LOKI_URL", "http://loki.aiops.svc.cluster.local:3100")
    TEMPO_URL: str = os.getenv("TEMPO_URL", "http://tempo.aiops.svc.cluster.local:3200")

    # Kubernetes API
    KUBECONFIG_PATH: str = os.getenv("KUBECONFIG_PATH", "")
    IN_CLUSTER: bool = os.getenv("KUBERNETES_SERVICE_HOST") is not None

    # Server settings
    PORT: int = int(os.getenv("PORT", "8000"))
    HOST: str = os.getenv("HOST", "0.0.0.0")
    APP_NAME: str = "K3s AIOps Platform"

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

settings = Settings()

