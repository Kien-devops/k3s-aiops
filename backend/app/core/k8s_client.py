import logging
import os
from typing import Dict, List, Any
from kubernetes import client, config
from app.config import settings

logger = logging.getLogger(__name__)

class K8sClient:
    def __init__(self):
        self._init_client()

    def _init_client(self):
        self.initialized = False
        try:
            if settings.IN_CLUSTER:
                config.load_incluster_config()
                self.initialized = True
                logger.info("Loaded in-cluster Kubernetes config.")
            elif settings.KUBECONFIG_PATH and os.path.exists(settings.KUBECONFIG_PATH):
                config.load_kube_config(config_file=settings.KUBECONFIG_PATH)
                self.initialized = True
                logger.info(f"Loaded kubeconfig from {settings.KUBECONFIG_PATH}")
            else:
                # Try default location or local repo kubeconfig
                local_kc = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "kubeconfig.yaml")
                if os.path.exists(local_kc):
                    config.load_kube_config(config_file=local_kc)
                    self.initialized = True
                    logger.info(f"Loaded kubeconfig from repo root: {local_kc}")
                else:
                    config.load_kube_config()
                    self.initialized = True
                    logger.info("Loaded default ~/.kube/config.")
        except Exception as e:
            logger.warning(f"Could not initialize Kubernetes client: {e}")
            self.initialized = False

        if self.initialized:
            self.core_v1 = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
        else:
            self.core_v1 = None
            self.apps_v1 = None

    def get_nodes(self) -> List[Dict[str, Any]]:
        if not self.initialized:
            return []
        try:
            nodes = self.core_v1.list_node().items
            result = []
            for n in nodes:
                # check ready condition
                ready = False
                for c in n.status.conditions or []:
                    if c.type == "Ready" and c.status == "True":
                        ready = True
                        break
                
                roles = []
                for label in n.metadata.labels or {}:
                    if "node-role.kubernetes.io/" in label:
                        roles.append(label.split("/")[-1])

                result.append({
                    "name": n.metadata.name,
                    "ready": ready,
                    "roles": roles or ["worker"],
                    "os": n.status.node_info.os_image,
                    "kubelet_version": n.status.node_info.kubelet_version,
                    "internal_ip": next((addr.address for addr in n.status.addresses if addr.type == "InternalIP"), None)
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching nodes: {e}")
            return []

    def get_pods(self, namespace: str = None) -> List[Dict[str, Any]]:
        if not self.initialized:
            return []
        try:
            if namespace:
                pod_list = self.core_v1.list_namespaced_pod(namespace).items
            else:
                pod_list = self.core_v1.list_pod_for_all_namespaces().items

            result = []
            for p in pod_list:
                restarts = 0
                ready_count = 0
                total_containers = len(p.status.container_statuses or [])
                if p.status.container_statuses:
                    for cs in p.status.container_statuses:
                        restarts += cs.restart_count
                        if cs.ready:
                            ready_count += 1

                # calculate phase/status
                phase = p.status.phase
                if p.metadata.deletion_timestamp:
                    phase = "Terminating"

                result.append({
                    "name": p.metadata.name,
                    "namespace": p.metadata.namespace,
                    "node": p.spec.node_name,
                    "status": phase,
                    "ready": f"{ready_count}/{total_containers}",
                    "is_ready": ready_count == total_containers and phase == "Running",
                    "restarts": restarts,
                    "pod_ip": p.status.pod_ip,
                    "created_at": str(p.metadata.creation_timestamp)
                })
            return result
        except Exception as e:
            logger.error(f"Error fetching pods: {e}")
            return []

    def get_recent_warning_events(self, limit: int = 15) -> List[Dict[str, Any]]:
        if not self.initialized:
            return []
        try:
            events = self.core_v1.list_event_for_all_namespaces(
                field_selector="type=Warning"
            ).items
            sorted_events = sorted(
                events,
                key=lambda x: str(x.last_timestamp or x.event_time or ""),
                reverse=True
            )[:limit]

            return [
                {
                    "namespace": e.metadata.namespace,
                    "reason": e.reason,
                    "message": e.message,
                    "object": f"{e.involved_object.kind}/{e.involved_object.name}",
                    "count": e.count,
                    "time": str(e.last_timestamp)
                }
                for e in sorted_events
            ]
        except Exception as e:
            logger.error(f"Error fetching events: {e}")
            return []

k8s_client = K8sClient()
