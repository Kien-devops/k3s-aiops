import tarfile
import os
import paramiko
import subprocess
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
TAR_PATH = os.path.join(REPO_ROOT, "backend_build.tar.gz")
KUBECONFIG = os.path.join(REPO_ROOT, "kubeconfig.yaml")

def package_backend():
    print("Packaging backend into tar.gz...")
    with tarfile.open(TAR_PATH, "w:gz") as tar:
        tar.add(BACKEND_DIR, arcname=".")
    print(f"Archive created: {TAR_PATH} ({os.path.getsize(TAR_PATH)} bytes)")

def deploy():
    package_backend()

    # Connect to server-tang2 to build Docker image
    print("Connecting to server-tang2 (100.98.92.34)...")
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect("100.98.92.34", port=22, username="node", password="kien1234@")

    # Upload tar
    print("Uploading archive...")
    sftp = c.open_sftp()
    sftp.put(TAR_PATH, "/tmp/backend_build.tar.gz")
    sftp.close()

    # Build image on tang2
    print("Extracting and building docker image on server-tang2...")
    build_cmds = """
    rm -rf /tmp/backend_src && mkdir -p /tmp/backend_src
    tar -xzf /tmp/backend_build.tar.gz -C /tmp/backend_src
    cd /tmp/backend_src
    echo kien1234@ | sudo -S docker build -t k3s-aiops-backend:latest .
    echo kien1234@ | sudo -S docker save k3s-aiops-backend:latest -o /tmp/k3s-aiops-backend.tar
    echo kien1234@ | sudo -S chmod 666 /tmp/k3s-aiops-backend.tar
    echo kien1234@ | sudo -S k3s ctr -n k8s.io images import /tmp/k3s-aiops-backend.tar
    echo "TANG2_DONE"
    """
    stdin, stdout, stderr = c.exec_command(build_cmds, get_pty=True)
    out = stdout.read().decode()
    print("Build output on tang2:\n", out[-1000:] if len(out) > 1000 else out)

    # Now copy tar to server-tang4 (worker node where pods run)
    print("Transferring image tar to server-tang4 (192.168.30.35) and importing into containerd...")
    import_cmds = """
    sshpass -p kien1234@ scp -o StrictHostKeyChecking=no /tmp/k3s-aiops-backend.tar node@192.168.30.35:/tmp/
    sshpass -p kien1234@ ssh -o StrictHostKeyChecking=no node@192.168.30.35 "echo kien1234@ | sudo -S k3s ctr -n k8s.io images import /tmp/k3s-aiops-backend.tar"
    echo "TANG4_DONE"
    """
    stdin, stdout, stderr = c.exec_command(import_cmds, get_pty=True)
    out = stdout.read().decode()
    print("Transfer output:\n", out)
    c.close()

    # Now apply 04-backend.yaml
    print("Applying 04-backend.yaml...")
    subprocess.run([
        "kubectl",
        f"--kubeconfig={KUBECONFIG}",
        "--insecure-skip-tls-verify=true",
        "apply",
        "-f",
        os.path.join(REPO_ROOT, "k8s", "04-backend.yaml")
    ])

    print("Checking rollout status...")
    subprocess.run([
        "kubectl",
        f"--kubeconfig={KUBECONFIG}",
        "--insecure-skip-tls-verify=true",
        "rollout",
        "status",
        "deployment/aiops-backend",
        "-n",
        "aiops",
        "--timeout=90s"
    ])

    # Clean local tar
    if os.path.exists(TAR_PATH):
        os.remove(TAR_PATH)

if __name__ == "__main__":
    deploy()
