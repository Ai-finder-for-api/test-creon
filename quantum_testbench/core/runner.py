"""
Test Suite automation runner.
Executes test collections with progress reporting, assertion tracking, and run statistics.
"""
import time
from typing import Callable, Optional
from quantum_testbench.models.data_models import (
    TestSuite, SuiteRunResult, TestResult
)
from quantum_testbench.core.client import HttpClient
from quantum_testbench.core.environment import EnvironmentManager


class SuiteRunner:
    def __init__(self, http_client: Optional[HttpClient] = None, env_manager: Optional[EnvironmentManager] = None):
        self.env_manager = env_manager or EnvironmentManager()
        self.http_client = http_client or HttpClient(env_manager=self.env_manager)

    def run_suite(
        self,
        suite: TestSuite,
        on_progress: Optional[Callable[[int, int, TestResult], None]] = None
    ) -> SuiteRunResult:
        start_time = time.time()
        start_perf = time.perf_counter()
        results = []
        passed_count = 0
        failed_count = 0

        total = len(suite.requests)

        for idx, req_def in enumerate(suite.requests, start=1):
            result = self.http_client.execute(req_def)
            results.append(result)

            if result.passed:
                passed_count += 1
            else:
                failed_count += 1

            if on_progress:
                on_progress(idx, total, result)

        duration_ms = (time.perf_counter() - start_perf) * 1000.0

        return SuiteRunResult(
            suite_id=suite.id,
            suite_name=suite.name,
            start_time=start_time,
            duration_ms=duration_ms,
            results=results,
            total_count=total,
            passed_count=passed_count,
            failed_count=failed_count
        )
