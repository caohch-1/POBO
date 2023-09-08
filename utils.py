from wrk2LoadGenerator import Wrk2LoadGenerator
from jaegerCollector import JaegerCollector
from k8sManager import K8sManager
from time import sleep, time

def interpolate_distribution(start_distribution, end_distribution, current_round, total_rounds):
    weight_start = (total_rounds - current_round) / total_rounds
    weight_end = 1 - weight_start

    interpolated_distribution = [
        weight_start * start_dist + weight_end * end_dist
        for start_dist, end_dist in zip(start_distribution, end_distribution)
    ]

    return interpolated_distribution


def reset_env(k8sManager, cpu: int = 50, mem: int = 100, replicas: int = 1):
    k8sManager.set_cpu("frontend", cpu, cpu)
    k8sManager.set_cpu("recommendation", cpu, cpu)
    k8sManager.set_cpu("search", cpu, cpu)
    k8sManager.set_cpu("user", cpu, cpu)
    k8sManager.set_cpu("rate", cpu, cpu)
    k8sManager.set_cpu("memcached-rate", cpu, cpu)
    k8sManager.set_cpu("profile", cpu, cpu)
    k8sManager.set_cpu("memcached-profile", cpu, cpu)
    k8sManager.set_cpu("geo", cpu, cpu)
    k8sManager.set_cpu("reservation", cpu, cpu)

    k8sManager.set_memory("frontend", mem, mem)
    k8sManager.set_memory("recommendation", mem, mem)
    k8sManager.set_memory("search", mem, mem)
    k8sManager.set_memory("user", mem, mem)
    k8sManager.set_memory("rate", mem, mem)
    k8sManager.set_memory("memcached-rate", mem, mem)
    k8sManager.set_memory("profile", mem, mem)
    k8sManager.set_memory("memcached-profile", mem, mem)
    k8sManager.set_memory("geo", mem, mem)
    k8sManager.set_memory("reservation", mem, mem)

    sleep(5)

    k8sManager.scale_deployment("frontend", replicas)
    k8sManager.scale_deployment("recommendation", replicas)
    k8sManager.scale_deployment("search", replicas)
    k8sManager.scale_deployment("user", replicas)
    k8sManager.scale_deployment("rate", replicas)
    k8sManager.scale_deployment("memcached-rate", replicas)
    k8sManager.scale_deployment("profile", replicas)
    k8sManager.scale_deployment("memcached-profile", replicas)
    k8sManager.scale_deployment("geo", replicas)
    k8sManager.scale_deployment("reservation", replicas)
    k8sManager.scale_deployment("memcached-reserve", replicas)
    k8sManager.scale_deployment("jaeger", 1)


def exp(rate: int, module: str, duration: str = "80s", sla: int = 1500):
    # WRK2
    command_path = "/home/caohch1/Downloads/Erms/wrk2/wrk"
    svc_url = "http://localhost:38547"
    task_type= ""
    script = "/home/caohch1/Downloads/Erms/wrk2/scripts/hotel-reservation/" + module + ".lua"
    if module == "search":
        task_type = "hotels"
        
    elif module == "login":
        task_type = "user"

    elif module == "recommendation":
        task_type = "recommendations"


    threads = 8
    connections = 16
    latency = True
    distribution = "exp"

    generator = Wrk2LoadGenerator(
        command_path, svc_url, duration, rate, threads, connections, latency, distribution, script)

    start_time = generator.generate_load()

    # # PROMETHEUS
    # namespace = "hotel-reserv"
    # prometheusHost = "http://localhost:30090"
    # namespace = "hotel-reserv"

    # prometheusCollector = PrometheusCollector(prometheusHost, namespace)
    # cpu_usage = prometheusCollector.get_cpu_usage(
    #     start_time, start_time+int(duration[:2]), int(duration[:2]))
    # mem_usage = prometheusCollector.get_mem_usage(
    #     start_time, start_time+int(duration[:2]))

    # JAEGER
    jaeger_url = "http://127.0.0.1:32961/api/traces"
    limit = 25000
    entry = "frontend"

    jaegerCollector = JaegerCollector(jaeger_url)
    avg_letency_jaeger, sla_violation_num, sla_violation, sla_latency, upper_latency = jaegerCollector.collect(
        start_time=start_time, duration=duration, limit=limit, service=entry, sla=sla, task_type=task_type)

    return start_time, avg_letency_jaeger, sla_violation_num, sla_violation, sla_latency, upper_latency, None, None