# Quantum TestBench

[![CI Test Suite](https://github.com/Ai-finder-for-api/test-creon/actions/workflows/ci.yml/badge.svg)](https://github.com/Ai-finder-for-api/test-creon/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Quality: Production QA](https://img.shields.io/badge/Quality-Production_QA-10b981.svg)]()

> **Quantum TestBench** is a native, lightweight, standalone desktop QA test automation workbench and API client with zero cloud dependencies, real-time assertion verification, concurrent load benchmarking, an integrated loopback mock server, and automated report generation.

---

## ✨ Features

- **🚀 Interactive API Tester**:
  - Full HTTP method support (GET, POST, PUT, DELETE, PATCH, HEAD).
  - Dynamic `{{ENVIRONMENT_VARIABLES}}` interpolation in URLs, headers, and bodies.
  - Granular QA assertions: HTTP status codes, latency thresholds, body substring matching, header validation, and nested JSON path comparisons (`data.user.name == 'Alice'`).
  - Response inspect with formatted pretty-printed JSON, headers breakdown, and microsecond latency measurement.

- **📋 Automated Test Suite Runner**:
  - Group tests into regression and functional test collections.
  - One-click suite execution with real-time progress tracking.
  - Detailed assertion failure diagnostics with visual status badges.

- **📡 Built-in Mock HTTP Server & Webhook Inspector**:
  - Embedded zero-config multi-threaded mock server running on loopback (`127.0.0.1:8765`).
  - Real-time inbound traffic logger: captures method, client IP, path, headers, and request payloads for debugging webhooks and callbacks.

- **⚡ High-Concurrency Load Benchmark**:
  - Multi-threaded load generation engine.
  - Calculates Requests-Per-Second (RPS), Min/Max/Avg latency, and percentile distributions (**p50, p90, p95, p99**).

- **📊 Comprehensive QA Reporting**:
  - Single-click export of test run results to self-contained dark-mode **HTML Reports**, machine-readable **JSON**, and **GitHub-flavored Markdown**.

- **🎨 Modern Native GUI**:
  - Built with CustomTkinter modern dark aesthetic.
  - High-DPI support, modular views, responsive layout, and zero telemetry.

---

## 🛠️ Installation & Quickstart

```bash
# Clone the repository
git clone https://github.com/Ai-finder-for-api/test-creon.git
cd test-creon

# Install dependencies
pip install -r requirements.txt

# Run the test suite
python3 -m unittest discover -s tests -p "test_*.py"

# Launch Quantum TestBench GUI
python3 quantum_testbench/app.py
```

---

## 📂 Project Structure

```
test-creon/
├── .github/workflows/ci.yml       # Automated GitHub Actions test workflow
├── quantum_testbench/             # Core application package
│   ├── app.py                     # Desktop GUI entry point
│   ├── models/                    # Typed dataclasses (Request, Assertion, Suite, Result)
│   ├── core/                      # Engine modules
│   │   ├── client.py              # HTTP execution & latency timer
│   │   ├── assertions.py          # QA assertion validation logic
│   │   ├── runner.py              # Automated test suite executor
│   │   ├── mock_server.py         # Multi-threaded loopback mock server
│   │   ├── load_tester.py         # Concurrent load bench
│   │   ├── reporter.py            # HTML/JSON/Markdown report generator
│   │   └── environment.py         # Variable interpolation manager
│   └── ui/                        # CustomTkinter interface
│       ├── main_window.py         # Main application window & navigation
│       └── views/                 # Modular tab views
└── tests/                         # Comprehensive unit test suite (100% passing)
```

---

## 🧪 Automated Testing

Quantum TestBench includes a 100% passing unit test suite verifying all core engine components:

```bash
$ python3 -m unittest discover -s tests -p "test_*.py"
................
Ran 16 tests in 1.829s

OK
```

---

## 📄 License

Licensed under the [MIT License](LICENSE).