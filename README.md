# K3s AIOps Platform 🚀

Autonomous On-Premises Kubernetes Observability & SRE Incident Copilot powered by **9Router GPT-5.6 Sol**.

![AIOps Architecture](https://raw.githubusercontent.com/Kien-devops/app1/master/docs/architecture.png)

## 📌 Architecture Overview

```text
┌────────────────────────────────────────────────────────┐
│                   AIOps Dashboard                      │
│      Next.js / Dark Glassmorphism SRE Copilot UI       │
│           (Health Score • Predictions • AI Chat)       │
└───────────────────────────┬────────────────────────────┘
                            │
┌───────────────────────────▼────────────────────────────┐
│         AI Analysis Backend — Python / FastAPI         │
│       Orchestrator • Context Builder • Incident Engine │
│ ┌──────────────────────────┐ ┌───────────────────────┐ │
│ │     Analytics Engine     │ │      LLM Gateway      │ │
│ │ Forecasting & Anomaly Det│ │ 9Router: GPT-5.6 Sol  │ │
│ └──────────────────────────┘ └───────────────────────┘ │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│              Observability Data Sources                │
│  • Prometheus (server-tang3:9090 - Metrics & RAPL Power)
│  • Loki (aiops/loki:3100 - Pod Logs via Promtail)      │
│  • Tempo & OpenTelemetry (aiops/tempo:3200 - Tracing)  │
│  • Kubernetes Core API (server-tang2:6443)             │
└───────────────────────────▲────────────────────────────┘
                            │
┌───────────────────────────┴────────────────────────────┐
│                    Your K3s Cluster                    │
│  • server-tang2: Control Plane                         │
│  • server-tang4: Worker (anhvan & microservices-demo)  │
│  • server-tang3: Observability Monitor                 │
└────────────────────────────────────────────────────────┘
```

## 🌐 Public Domain & Routes

The platform is routed via Cloudflare / Reverse Proxy Tunnel:
* **Dashboard & API**: `https://aiops.onprem.site`
* **Prometheus Targets**: `http://100.112.150.56:9090`
* **English Learning App**: `https://anhvan.onprem.site`
* **Microservices Demo App**: `https://app1.onprem.site`

## 🧠 LLM Gateway Configuration

Configured to use **9Router** with **GPT-5.6 Sol**:
* **Endpoint**: `https://9router.onprem.site/v1`
* **Model**: `gpt-5.6-sol` (alias `cx/gpt-5.6-sol`)
* **Secret**: Managed via `k8s/02-secrets.yaml` (ignored in git for security)

## 📁 Repository Structure

```
.
├── backend/                  # FastAPI AI Analysis Backend
│   ├── app/
│   │   ├── api/              # API Endpoints (Health, Cluster, Analysis, Chat)
│   │   ├── analytics/        # Health Score & Anomaly Detection Engines
│   │   ├── core/             # Context Builder, LLM Gateway, K8s Client
│   │   └── datasources/      # Prometheus, Loki, Tempo connectors
│   ├── static/               # Standalone embedded dark-mode dashboard
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                 # Modern Next.js 15 Tailwind SRE Copilot UI
│   ├── src/app/
│   ├── Dockerfile
│   └── package.json
├── k8s/                      # Kubernetes manifests
│   ├── 00-namespace.yaml
│   ├── 01-rbac.yaml
│   ├── 02-secrets.yaml.example
│   ├── 03-observability/     # Loki, Promtail, Tempo, OTel Collector
│   ├── 04-backend.yaml
│   └── 05-ingress.yaml
└── scripts/
    ├── build_and_deploy_backend.py
    └── deploy_k8s.py
```

## 🚀 Quick Deployment to K3s

1. Create `k8s/02-secrets.yaml` from example:
```bash
cp k8s/02-secrets.yaml.example k8s/02-secrets.yaml
# Edit router-key with your 9router token
```

2. Deploy all manifests:
```bash
python scripts/deploy_k8s.py
```

3. Build and roll out backend:
```bash
python scripts/build_and_deploy_backend.py
```

4. Access dashboard:
Open browser at `https://aiops.onprem.site`
