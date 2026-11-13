"""
Data models for Quantum TestBench QA Studio.
Defines strongly typed structures for requests, responses, assertions, test suites, and load metrics.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any
import time


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"


class AssertionType(str, Enum):
    STATUS_EQUALS = "status_equals"
    LATENCY_LESS_THAN = "latency_less_than"
    BODY_CONTAINS = "body_contains"
    JSON_PATH_EQUALS = "json_path_equals"
    HEADER_EXISTS = "header_exists"


@dataclass
class Assertion:
    assertion_type: AssertionType
    expected_value: Any
    actual_value: Optional[Any] = None
    passed: bool = False
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.assertion_type.value,
            "expected": self.expected_value,
            "actual": self.actual_value,
            "passed": self.passed,
            "message": self.message
        }


@dataclass
class RequestDefinition:
    id: str
    name: str
    method: HttpMethod = HttpMethod.GET
    url: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    assertions: List[Assertion] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "method": self.method.value,
            "url": self.url,
            "headers": self.headers,
            "body": self.body,
            "assertions": [a.to_dict() for a in self.assertions]
        }


@dataclass
class ResponseData:
    status_code: int
    status_text: str
    headers: Dict[str, str]
    body: str
    elapsed_ms: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status_code": self.status_code,
            "status_text": self.status_text,
            "headers": self.headers,
            "body": self.body,
            "elapsed_ms": round(self.elapsed_ms, 2),
            "timestamp": self.timestamp
        }


@dataclass
class TestResult:
    request: RequestDefinition
    response: Optional[ResponseData] = None
    assertion_results: List[Assertion] = field(default_factory=list)
    passed: bool = False
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request": self.request.to_dict(),
            "response": self.response.to_dict() if self.response else None,
            "assertion_results": [a.to_dict() for a in self.assertion_results],
            "passed": self.passed,
            "error": self.error
        }


@dataclass
class TestSuite:
    id: str
    name: str
    description: str = ""
    requests: List[RequestDefinition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "requests": [r.to_dict() for r in self.requests]
        }


@dataclass
class SuiteRunResult:
    suite_id: str
    suite_name: str
    start_time: float
    duration_ms: float
    results: List[TestResult] = field(default_factory=list)
    total_count: int = 0
    passed_count: int = 0
    failed_count: int = 0

    @property
    def pass_percentage(self) -> float:
        if self.total_count == 0:
            return 0.0
        return round((self.passed_count / self.total_count) * 100.0, 1)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "suite_name": self.suite_name,
            "start_time": self.start_time,
            "duration_ms": round(self.duration_ms, 2),
            "total_count": self.total_count,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "pass_percentage": self.pass_percentage,
            "results": [r.to_dict() for r in self.results]
        }


@dataclass
class LoadTestConfig:
    url: str
    method: HttpMethod = HttpMethod.GET
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[str] = None
    concurrency: int = 10
    total_requests: int = 100
    timeout_sec: float = 10.0


@dataclass
class LoadTestResult:
    total_requests: int
    successful_requests: int
    failed_requests: int
    total_duration_sec: float
    rps: float
    min_latency_ms: float
    max_latency_ms: float
    avg_latency_ms: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    status_distribution: Dict[int, int] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "total_duration_sec": round(self.total_duration_sec, 3),
            "rps": round(self.rps, 1),
            "min_latency_ms": round(self.min_latency_ms, 2),
            "max_latency_ms": round(self.max_latency_ms, 2),
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "p50_ms": round(self.p50_ms, 2),
            "p90_ms": round(self.p90_ms, 2),
            "p95_ms": round(self.p95_ms, 2),
            "p99_ms": round(self.p99_ms, 2),
            "status_distribution": self.status_distribution
        }
