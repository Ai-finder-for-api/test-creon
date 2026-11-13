"""
High-performance HTTP execution engine for QA test requests.
Handles environment variable interpolation, precise latency measurement, and assertion evaluation.
"""
import time
import requests
from typing import Optional
from quantum_testbench.models.data_models import (
    RequestDefinition, ResponseData, TestResult, HttpMethod
)
from quantum_testbench.core.environment import EnvironmentManager
from quantum_testbench.core.assertions import AssertionEngine


class HttpClient:
    def __init__(self, env_manager: Optional[EnvironmentManager] = None, timeout: float = 15.0):
        self.env_manager = env_manager or EnvironmentManager()
        self.timeout = timeout
        self.session = requests.Session()

    def execute(self, req_def: RequestDefinition) -> TestResult:
        # Interpolate variables
        resolved_url = self.env_manager.interpolate(req_def.url) or ""
        resolved_headers = self.env_manager.interpolate_dict(req_def.headers)
        resolved_body = self.env_manager.interpolate(req_def.body)

        start_time = time.perf_counter()
        resp_data: Optional[ResponseData] = None
        error_msg: Optional[str] = None

        try:
            method_str = req_def.method.value if isinstance(req_def.method, HttpMethod) else str(req_def.method)
            req_kwargs = {
                "method": method_str,
                "url": resolved_url,
                "headers": resolved_headers,
                "timeout": self.timeout,
                "allow_redirects": True
            }

            if resolved_body and method_str in ("POST", "PUT", "PATCH", "DELETE"):
                req_kwargs["data"] = resolved_body.encode("utf-8")

            res = self.session.request(**req_kwargs)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            resp_data = ResponseData(
                status_code=res.status_code,
                status_text=res.reason or "OK",
                headers=dict(res.headers),
                body=res.text,
                elapsed_ms=elapsed_ms
            )

        except requests.exceptions.RequestException as e:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            error_msg = str(e)
            resp_data = None

        # Evaluate QA assertions
        evaluated_assertions = []
        all_passed = True if (resp_data is not None and not error_msg) else False

        if req_def.assertions:
            for ast in req_def.assertions:
                eval_ast = AssertionEngine.evaluate(ast, resp_data)
                evaluated_assertions.append(eval_ast)
                if not eval_ast.passed:
                    all_passed = False
        else:
            # If no explicit assertions, consider successful if HTTP 2xx
            if resp_data:
                all_passed = (200 <= resp_data.status_code < 300)

        return TestResult(
            request=req_def,
            response=resp_data,
            assertion_results=evaluated_assertions,
            passed=all_passed,
            error=error_msg
        )
