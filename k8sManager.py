from kubernetes import client, config
from time import sleep


class K8sManager:
    def __init__(self, namespace):
        # Load the Kubernetes configuration
        config.load_kube_config()

        # Create the Kubernetes API client
        self.api_client_corev1 = client.CoreV1Api()
        self.api_client_appsv1 = client.AppsV1Api()
        self.namespace = namespace

        self.pod_list = self.api_client_corev1.list_namespaced_pod(
            namespace=self.namespace)
        self.service_list = self.api_client_corev1.list_namespaced_service(
            namespace=self.namespace)
        self.deployment_list = self.api_client_appsv1.list_namespaced_deployment(
            namespace=self.namespace)

    # Update the list of pods, services, and deployments
    def update(self):
        self.pod_list = self.api_client_corev1.list_namespaced_pod(
            namespace=self.namespace)
        self.service_list = self.api_client_corev1.list_namespaced_service(
            namespace=self.namespace)
        self.deployment_list = self.api_client_appsv1.list_namespaced_deployment(
            namespace=self.namespace)

    # Get the list of pods' name
    def get_pods_name_list(self):
        return [pod.metadata.name for pod in self.pod_list.items]

    # Get the list of services' name
    def scale_deployment(self, deployment_name, replica_num):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        if deployment.spec.replicas != replica_num:
            deployment.spec.replicas = replica_num
            self.api_client_appsv1.patch_namespaced_deployment_scale(
                    name=deployment_name, namespace=self.namespace, body=deployment)
            # Wait for the deployment to finish
            while True:
                deployment = self.api_client_appsv1.read_namespaced_deployment(
                    deployment_name, self.namespace)
                # Check if all replicas are available and the rollout is complete
                if (
                    deployment.status.available_replicas == deployment.spec.replicas
                    and deployment.status.replicas == deployment.spec.replicas
                    and deployment.status.updated_replicas == deployment.spec.replicas
                ):
                    break
            print(
                f"[K8sManager Scale] Scale {deployment_name} to {replica_num} pods.")
            sleep(1)
        else:
            print(
                f"[K8sManager Scale] Keep {deployment_name} have {replica_num} pods.")

    # Set the limit cpu of a deployment
    def set_limit_cpu(self, deployment_name, cpu_limit):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        old_cpu_limit = deployment.spec.template.spec.containers[0].resources.limits["cpu"]
        deployment.spec.template.spec.containers[0].resources.limits["cpu"] = cpu_limit
        self.api_client_appsv1.patch_namespaced_deployment(
            name=deployment_name, namespace=self.namespace, body=deployment)
        print(
            f"[K8sManager Limit] Set {deployment_name} limit cpu from {old_cpu_limit} to {cpu_limit}.")

    # Set the request cpu of a deployment

    def set_request_cpu(self, deployment_name, cpu_request):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        old_cpu_request = deployment.spec.template.spec.containers[0].resources.requests["cpu"]
        deployment.spec.template.spec.containers[0].resources.requests["cpu"] = cpu_request
        self.api_client_appsv1.patch_namespaced_deployment(
            name=deployment_name, namespace=self.namespace, body=deployment)
        print(
            f"[K8sManager Request] Set {deployment_name} request cpu from {old_cpu_request} to {cpu_request}.")

    # Set the limit memory of a deployment
    def set_limit_memory(self, deployment_name, memory_limit):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        old_memory_limit = deployment.spec.template.spec.containers[0].resources.limits["memory"]
        deployment.spec.template.spec.containers[0].resources.limits["memory"] = memory_limit
        self.api_client_appsv1.patch_namespaced_deployment(
            name=deployment_name, namespace=self.namespace, body=deployment)
        print(
            f"[K8sManager Limit] Set {deployment_name} limit memory from {old_memory_limit} to {memory_limit}.")

    # Set the request memory of a deployment

    def set_request_memory(self, deployment_name, memory_request):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        old_memory_request = deployment.spec.template.spec.containers[
            0].resources.requests["memory"]
        deployment.spec.template.spec.containers[0].resources.requests["memory"] = memory_request
        self.api_client_appsv1.patch_namespaced_deployment(
            name=deployment_name, namespace=self.namespace, body=deployment)
        print(
            f"[K8sManager Request] Set {deployment_name} request memory from {old_memory_request} to {memory_request}.")

    def set_cpu(self, deployment_name, cpu_limit, cpu_request):
        cpu_limit = f"{cpu_limit}m"
        cpu_request = f"{cpu_request}m"

        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        deployment.spec.template.spec.containers[0].resources.limits["cpu"] = cpu_limit
        deployment.spec.template.spec.containers[0].resources.requests["cpu"] = cpu_request

        self.api_client_appsv1.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment)

        print(
            f"[K8sManager Limit] Set {deployment_name} limit cpu to {cpu_limit}.")
        print(
            f"[K8sManager Request] Set {deployment_name} request cpu to {cpu_request}.")
        sleep(1)
        

    def set_memory(self, deployment_name, memory_limit, memory_request):
        memory_limit = f"{memory_limit}Mi"
        memory_request = f"{memory_request}Mi"

        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        deployment.spec.template.spec.containers[0].resources.limits["memory"] = memory_limit
        deployment.spec.template.spec.containers[0].resources.requests["memory"] = memory_request
        self.api_client_appsv1.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment)
        print(
            f"[K8sManager Limit] Set {deployment_name} limit memory to {memory_limit}.")
        print(
            f"[K8sManager Request] Set {deployment_name} request memory to {memory_request}.")
        sleep(1)
