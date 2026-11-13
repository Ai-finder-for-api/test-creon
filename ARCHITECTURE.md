# Architecture & Technical Design

**Quantum TestBench** is engineered as an enterprise-grade QA and API verification workbench built with Python 3 and modern retained-mode CustomTkinter.

## Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│               Quantum TestBench UI Layer               │
│  (MainWindow, ApiView, SuiteView, LoadView, MockView)  │
└───────────────┬────────────────────────┬───────────────┘
                │                        │
┌───────────────▼────────┐      ┌────────▼───────────────┐
│     Core Runner &      │      │  Async HTTP Client &   │
│   Assertion Engine     │      │   Environment Engine   │
└───────────────┬────────┘      └────────┬───────────────┘
                │                        │
┌───────────────▼────────────────────────▼───────────────┐
│       Built-in Multi-threaded Mock HTTP Server         │
│         (127.0.0.1:8765 Loopback Sandbox)              │
└────────────────────────────────────────────────────────┘
```

### Subsystems

1. **HTTP Client & Assertion Engine (`quantum_testbench.core`)**:
   - `HttpClient`: Session-pooled connection manager with microsecond precision round-trip latency timers.
   - `AssertionEngine`: Pure-function verification logic supporting `status_equals`, `latency_less_than`, `body_contains`, `header_exists`, and dotted `json_path_equals`.
   - `EnvironmentManager`: Regex token interpolator substituting `{{VAR_NAME}}` across URLs, headers, and request payloads.

2. **Test Automation & Suite Runner (`quantum_testbench.core.runner`)**:
   - Executes ordered collections of QA test cases.
   - Emits real-time progress callbacks for GUI animation.
   - Computes statistical summaries (Pass percentage, Total execution time, Pass/Fail breakdowns).

3. **Built-in Mock HTTP Server (`quantum_testbench.core.mock_server`)**:
   - Multi-threaded loopback HTTP daemon.
   - Intercepts inbound webhooks, logs all request headers and bodies, and responds with registered mock payloads.

4. **Concurrent Load Bench (`quantum_testbench.core.load_tester`)**:
   - `ThreadPoolExecutor` worker pool.
   - Gathers latency distributions and computes p50, p90, p95, and p99 percentiles along with Requests-Per-Second (RPS).

5. **Report Exporter (`quantum_testbench.core.reporter`)**:
   - Generates responsive HTML reports, structured JSON schemas, and formatted GitHub-flavored Markdown.