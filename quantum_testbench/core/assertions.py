"""
QA Assertion evaluation engine for automated API validation.
Provides granular checks on status codes, latency, headers, body text, and nested JSON fields.
"""
import json
from typing import Any, Optional
from quantum_testbench.models.data_models import (
    Assertion, AssertionType, ResponseData
)


class AssertionEngine:
    @staticmethod
    def evaluate(assertion: Assertion, response: Optional[ResponseData]) -> Assertion:
        if response is None:
            assertion.passed = False
            assertion.actual_value = None
            assertion.message = "Request failed or no response received"
            return assertion

        try:
            if assertion.assertion_type == AssertionType.STATUS_EQUALS:
                actual = int(response.status_code)
                expected = int(assertion.expected_value)
                assertion.actual_value = actual
                assertion.passed = (actual == expected)
                assertion.message = (
                    f"Status {actual} == {expected}"
                    if assertion.passed
                    else f"Expected status {expected}, received {actual}"
                )

            elif assertion.assertion_type == AssertionType.LATENCY_LESS_THAN:
                actual = round(response.elapsed_ms, 2)
                expected = float(assertion.expected_value)
                assertion.actual_value = f"{actual}ms"
                assertion.passed = (actual < expected)
                assertion.message = (
                    f"Response time {actual}ms < {expected}ms"
                    if assertion.passed
                    else f"Response time {actual}ms exceeded threshold {expected}ms"
                )

            elif assertion.assertion_type == AssertionType.BODY_CONTAINS:
                expected_str = str(assertion.expected_value)
                assertion.actual_value = f"Length {len(response.body)} chars"
                assertion.passed = (expected_str in response.body)
                assertion.message = (
                    f"Response body contains '{expected_str}'"
                    if assertion.passed
                    else f"Response body does not contain '{expected_str}'"
                )

            elif assertion.assertion_type == AssertionType.HEADER_EXISTS:
                expected_header = str(assertion.expected_value).lower().strip()
                headers_lower = {k.lower(): v for k, v in response.headers.items()}
                assertion.passed = (expected_header in headers_lower)
                assertion.actual_value = headers_lower.get(expected_header, "<not present>")
                assertion.message = (
                    f"Header '{assertion.expected_value}' present"
                    if assertion.passed
                    else f"Header '{assertion.expected_value}' not found in response"
                )

            elif assertion.assertion_type == AssertionType.JSON_PATH_EQUALS:
                # Format: "key.path:expected_value"
                val_spec = str(assertion.expected_value)
                if ":" in val_spec:
                    path, exp_val = val_spec.split(":", 1)
                    path = path.strip()
                    exp_val = exp_val.strip()
                else:
                    path = val_spec.strip()
                    exp_val = None

                try:
                    data = json.loads(response.body)
                    parts = path.split(".")
                    curr = data
                    for part in parts:
                        if isinstance(curr, dict) and part in curr:
                            curr = curr[part]
                        elif isinstance(curr, list) and part.isdigit() and int(part) < len(curr):
                            curr = curr[int(part)]
                        else:
                            curr = None
                            break

                    assertion.actual_value = str(curr)
                    if exp_val is not None:
                        assertion.passed = (str(curr).lower() == exp_val.lower())
                        assertion.message = (
                            f"JSON path '{path}' == '{exp_val}'"
                            if assertion.passed
                            else f"JSON path '{path}' was '{curr}', expected '{exp_val}'"
                        )
                    else:
                        assertion.passed = (curr is not None)
                        assertion.message = (
                            f"JSON path '{path}' exists"
                            if assertion.passed
                            else f"JSON path '{path}' not found"
                        )
                except Exception as ex:
                    assertion.passed = False
                    assertion.actual_value = f"Parse Error: {ex}"
                    assertion.message = f"Failed to parse body as JSON for path '{path}'"

            else:
                assertion.passed = False
                assertion.message = f"Unsupported assertion type: {assertion.assertion_type}"

        except Exception as err:
            assertion.passed = False
            assertion.actual_value = f"Exception: {err}"
            assertion.message = f"Assertion evaluation failed: {err}"

        return assertion
