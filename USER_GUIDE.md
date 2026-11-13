# Quantum TestBench User Guide

## Getting Started

1. **Launch the Application**:
   ```bash
   python3 quantum_testbench/app.py
   ```

2. **Execute Single Request**:
   - Navigate to **🚀 API Tester** in the sidebar.
   - Set Method (e.g. `GET`), URL (e.g. `{{BASE_URL}}/api/v1/users`).
   - Add automated assertions in the QA Assertions tab:
     ```
     STATUS:200
     LATENCY:500
     CONTAINS:Alice
     ```
   - Click **Send Request 🚀**.

3. **Run Automated Test Suites**:
   - Click **📋 Test Suites**.
   - Select a suite (e.g., *Health & Core Readiness Suite* or *Complete System Regression Test*).
   - Click **▶ Run Entire Suite**.
   - Review passing checks, failed assertions, and timing breakdowns.
   - Click **📥 Export Report** to export an HTML report.

4. **Run Performance / Load Benchmarks**:
   - Click **⚡ Load Bench**.
   - Set concurrency (e.g., 8 workers) and total requests (e.g., 50 requests).
   - Click **⚡ Run Load Benchmark** to calculate latency percentiles (p50, p90, p95, p99) and RPS.

5. **Inspect Live Webhooks**:
   - Click **📡 Mock Server & Logs**.
   - Send any POST / webhook to `http://127.0.0.1:8765/my-webhook`.
   - Inspect the real-time stream of incoming requests.