#!/usr/bin/env python3
import os
import subprocess
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KUBECONFIG = os.path.join(REPO_ROOT, "kubeconfig.yaml")

def run_kubectl(manifest_path):
    print(f"Applying: {manifest_path}...")
    cmd = [
        "kubectl",
        f"--kubeconfig={KUBECONFIG}",
        "--insecure-skip-tls-verify=true",
        "apply",
        "-f",
        manifest_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR applying {manifest_path}:\n{result.stderr}")
    else:
        print(result.stdout.strip())

def main():
    print("=== DEPLOYING K3S AIOPS PLATFORM ===")
    
    # 1. Namespace
    run_kubectl(os.path.join(REPO_ROOT, "k8s", "00-namespace.yaml"))
    
    # 2. RBAC
    run_kubectl(os.path.join(REPO_ROOT, "k8s", "01-rbac.yaml"))
    
    # 3. Secret
    secret_path = os.path.join(REPO_ROOT, "k8s", "02-secrets.yaml")
    if os.path.exists(secret_path):
        run_kubectl(secret_path)
    else:
        print("Note: k8s/02-secrets.yaml not found, please create from 02-secrets.yaml.example")

    # 4. Observability Stack
    obs_dir = os.path.join(REPO_ROOT, "k8s", "03-observability")
    for f in sorted(os.listdir(obs_dir)):
        if f.endswith(".yaml") or f.endswith(".yml"):
            run_kubectl(os.path.join(obs_dir, f))

    # 5. Ingress
    run_kubectl(os.path.join(REPO_ROOT, "k8s", "05-ingress.yaml"))

    print("\n=== CLUSTER AIOPS NAMESPACE STATUS ===")
    subprocess.run([
        "kubectl",
        f"--kubeconfig={KUBECONFIG}",
        "--insecure-skip-tls-verify=true",
        "get",
        "pods,svc,ingress",
        "-n",
        "aiops"
    ])

if __name__ == "__main__":
    main()
