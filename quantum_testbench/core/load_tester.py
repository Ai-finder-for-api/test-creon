import time
import requests
import statistics
from typing import Optional, Callable, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from quantum_testbench.models.data_models import LoadTestConfig, LoadTestResult, HttpMethod


class LoadTestRunner:
    def __init__(self):
        self._cancel_requested = False

    def cancel(self):
        self._cancel_requested = True

    def run(
        self,
        config: LoadTestConfig,
        on_progress: Optional[Callable[[int, int], None]] = None
    ) -> LoadTestResult:
        self._cancel_requested = False
        latencies: List[float] = []
        status_counts: Dict[int, int] = {}
        successful_count = 0
        failed_count = 0

        method_str = config.method.value if isinstance(config.method, HttpMethod) else str(config.method)
        session = requests.Session()

        def make_single_request():
            if self._cancel_requested:
                return None, 0.0, "cancelled"
            t0 = time.perf_counter()
            try:
                res = session.request(
                    method=method_str,
                    url=config.url,
                    headers=config.headers,
                    data=config.body.encode("utf-8") if config.body else None,
                    timeout=config.timeout_sec
                )
                dt = (time.perf_counter() - t0) * 1000.0
                return res.status_code, dt, None
            except Exception as ex:
                dt = (time.perf_counter() - t0) * 1000.0
                return None, dt, str(ex)

        start_time = time.perf_counter()
        completed = 0

        with ThreadPoolExecutor(max_workers=config.concurrency) as pool:
            futures = [pool.submit(make_single_request) for _ in range(config.total_requests)]
            for fut in as_completed(futures):
                if self._cancel_requested:
                    break
                status, latency, err = fut.result()
                completed += 1
                latencies.append(latency)

                if status is not None:
                    status_counts[status] = status_counts.get(status, 0) + 1
                    if 200 <= status < 400:
                        successful_count += 1
                    else:
                        failed_count += 1
                else:
                    failed_count += 1

                if on_progress:
                    on_progress(completed, config.total_requests)

        total_duration = time.perf_counter() - start_time
        if not latencies:
            latencies = [0.0]

        sorted_latencies = sorted(latencies)
        n = len(sorted_latencies)

        def get_percentile(p: float) -> float:
            idx = int(p * n)
            idx = max(0, min(n - 1, idx))
            return sorted_latencies[idx]

        rps = (completed / total_duration) if total_duration > 0 else 0.0

        return LoadTestResult(
            total_requests=completed,
            successful_requests=successful_count,
            failed_requests=failed_count,
            total_duration_sec=total_duration,
            rps=rps,
            min_latency_ms=sorted_latencies[0],
            max_latency_ms=sorted_latencies[-1],
            avg_latency_ms=statistics.mean(latencies),
            p50_ms=get_percentile(0.50),
            p90_ms=get_percentile(0.90),
            p95_ms=get_percentile(0.95),
            p99_ms=get_percentile(0.99),
            status_distribution=status_counts
        )