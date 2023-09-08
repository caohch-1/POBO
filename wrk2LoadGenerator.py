import subprocess
import re
from typing import List
from time import time
import threading

class Wrk2LoadGenerator:
    def __init__(self, command_path, url, duration="30s", rate=25, threads=4, connections=100, latency=True, distribution="exp", script=None):
        self.command_path = command_path
        self.url = url
        self.duration = duration
        self.rate = rate
        self.threads = threads
        self.connections = connections
        self.latency = latency
        self.distribution = distribution
        self.result = None
        self.total_requests = 0
        self.avg_latency = 0
        self.timeout_requests = 0
        self.script = script

    def generate_load(self):
        # set the command and parameters for wrk2
        params = ["-t", str(self.threads), "-c", str(self.connections),
                  "-d", self.duration, "-R", str(self.rate), self.url]
        
        if self.script:
            params.extend(["-s", self.script])
        
        if self.latency:
            params.append("-L")

        if self.distribution:
            params.extend(["-D", self.distribution])
            # params.append("-q")

        # run the wrk2 command
        command = [self.command_path] + params
        print(f"[Wrk2 Command] "+" ".join(command))

        start_time = time()
        result = subprocess.run(
            command, capture_output=True, text=True, check=True)
        
        # extract the number of requests, average latency, and timeout requests from the output
        match_requests = re.search(r"(\d+)\srequests", result.stdout)
        self.total_requests = int(match_requests.group(1))

        match_latency = re.search(r"Latency\s+(\d+\.\d+)", result.stdout)
        if match_latency:
            self.avg_latency = float(match_latency.group(1))
        else:
            self.avg_latency = 0  # Unknown latency

        match_timeouts = re.search(r"timeout\s+(\d+)", result.stdout)
        if match_timeouts:
            self.timeout_requests = int(match_timeouts.group(1))
        else:
            self.timeout_requests = 0

        print(f"[Wrk2 Res] Sent {self.total_requests} requests in {self.duration} with an average latency of {self.avg_latency*1000:.2f} us and {self.timeout_requests} timeouts.")

        return start_time

