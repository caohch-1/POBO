import requests
import json
import numpy as np



class JaegerCollector:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    # Collect traces from Jaeger
    def collect(self, start_time, duration, limit, service, sla, task_type):
        request_data = {
            "start": int(start_time * 1000000),
            "end": int((start_time + int(duration[:2]) * 1000) * 1000000),
            "operation": f"HTTP GET /{task_type}",
            "limit": limit,
            "service": service,
            "tags": '{"http.status_code":"200"}'
        }

        response = requests.get(self.endpoint, params=request_data)
        traces = json.loads(response.content)["data"]

        # Calculate average latency
        trace_durations = []
        for trace in traces:
            trace_duration = max([int(span["duration"]) for span in trace["spans"]])
            trace_durations.append(trace_duration)
        if len(trace_durations) > 0:
            trace_durations = np.array(trace_durations)
            trace_duration = trace_durations.sort()
            
            filtered_trace_durations = trace_durations[:int(len(trace_durations)*0.9)]
            average_latency = sum(filtered_trace_durations) / len(filtered_trace_durations) if len(filtered_trace_durations) != 0 else 0

            sla_violation_trace_durations = [x for x in trace_durations if x >= sla]
            sla_violations_latency = sum(sla_violation_trace_durations) / len(sla_violation_trace_durations) if len(sla_violation_trace_durations) != 0 else 0
            
            tail_trace_durations = trace_durations[int(len(trace_durations)*0.9):]
            tail_latency = sum(tail_trace_durations) / len(tail_trace_durations)

            print(
                f"[Jaeger] {len(filtered_trace_durations)} Normal<90\% latency is {average_latency/1000} ms.")
            print(f"[Jaeger] {len(sla_violation_trace_durations)}({len(sla_violation_trace_durations)/len(trace_durations)*100:.2f}%) traces violate SLA with an average latency of {sla_violations_latency/1000} ms.")
            print(f"[Jaeger] {len(tail_trace_durations)} Tail>90\% latency is {tail_latency/1000} ms.")
        else:
            print("[Jaeger] No traces found.")
            return 0, 0, 0, 0, 0

        return average_latency, len(sla_violation_trace_durations), len(sla_violation_trace_durations)/len(trace_durations)*100, sla_violations_latency, tail_latency
