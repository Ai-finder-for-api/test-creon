import json
import time
from typing import Dict, Any
from quantum_testbench.models.data_models import SuiteRunResult, TestResult


class ReportGenerator:
    @staticmethod
    def to_json(run_result: SuiteRunResult, indent: int = 2) -> str:
        return json.dumps(run_result.to_dict(), indent=indent)

    @staticmethod
    def to_markdown(run_result: SuiteRunResult) -> str:
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(run_result.start_time))
        lines = [
            f"# QA Test Execution Report: {run_result.suite_name}",
            f"- **Execution Timestamp**: {date_str}",
            f"- **Total Duration**: {round(run_result.duration_ms, 2)} ms",
            f"- **Pass Rate**: {run_result.pass_percentage}% ({run_result.passed_count}/{run_result.total_count})",
            "",
            "## Summary Metrics",
            f"| Total | Passed | Failed | Duration |",
            f"|---|---|---|---|",
            f"| {run_result.total_count} | {run_result.passed_count} | {run_result.failed_count} | {round(run_result.duration_ms, 2)}ms |",
            "",
            "## Detailed Results",
            "| # | Test Name | Method | URL | Status | Latency | Result |",
            "|---|---|---|---|---|---|---|"
        ]

        for i, res in enumerate(run_result.results, 1):
            req = res.request
            resp = res.response
            badge = "PASSED" if res.passed else "FAILED"
            status_code = resp.status_code if resp else "N/A"
            latency = f"{round(resp.elapsed_ms, 1)}ms" if resp else "ERR"
            lines.append(f"| {i} | {req.name} | `{req.method}` | `{req.url}` | {status_code} | {latency} | **{badge}** |")

            if res.assertion_results:
                for ast in res.assertion_results:
                    ast_status = "PASS" if ast.passed else "FAIL"
                    lines.append(f"  - [{ast_status}] {ast.message}")

        return "\n".join(lines)

    @staticmethod
    def to_html(run_result: SuiteRunResult) -> str:
        date_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(run_result.start_time))
        badge_color = "#10b981" if run_result.failed_count == 0 else "#ef4444"

        rows = []
        for i, res in enumerate(run_result.results, 1):
            req = res.request
            resp = res.response
            is_pass = res.passed
            status_class = "badge-pass" if is_pass else "badge-fail"
            status_text = "PASSED" if is_pass else "FAILED"
            status_code = resp.status_code if resp else "-"
            latency = f"{round(resp.elapsed_ms, 1)} ms" if resp else "Error"

            ast_html = ""
            if res.assertion_results:
                ast_items = []
                for a in res.assertion_results:
                    cls = "ast-pass" if a.passed else "ast-fail"
                    ast_items.append(f"<li class='{cls}'>{a.message}</li>")
                ast_html = f"<ul class='ast-list'>{''.join(ast_items)}</ul>"

            rows.append(f"""
            <tr>
                <td>{i}</td>
                <td><strong>{req.name}</strong></td>
                <td><span class="method-badge method-{req.method.lower()}">{req.method}</span></td>
                <td><code>{req.url}</code></td>
                <td>{status_code}</td>
                <td>{latency}</td>
                <td><span class="{status_class}">{status_text}</span></td>
            </tr>
            """)
            if ast_html:
                rows.append(f"""
                <tr class="details-row"><td colspan="7">{ast_html}</td></tr>
                """)

        table_rows = "\n".join(rows)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Quantum QA Report - {run_result.suite_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #334155; padding-bottom: 16px; margin-bottom: 24px; }}
        h1 {{ margin: 0; font-size: 24px; color: #38bdf8; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 28px; }}
        .stat-card {{ background: #1e293b; border-radius: 8px; padding: 18px; border: 1px solid #334155; }}
        .stat-card .label {{ font-size: 13px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-card .value {{ font-size: 28px; font-weight: bold; margin-top: 6px; }}
        table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 8px; overflow: hidden; }}
        th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #334155; }}
        th {{ background: #0f172a; color: #94a3b8; font-size: 13px; text-transform: uppercase; }}
        code {{ background: #0f172a; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 12px; }}
        .badge-pass {{ background: #065f46; color: #34d399; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .badge-fail {{ background: #7f1d1d; color: #f87171; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }}
        .method-badge {{ padding: 3px 6px; border-radius: 4px; font-size: 11px; font-weight: bold; font-family: monospace; }}
        .method-get {{ background: #0369a1; color: #e0f2fe; }}
        .method-post {{ background: #047857; color: #d1fae5; }}
        .method-put {{ background: #b45309; color: #fef3c7; }}
        .method-delete {{ background: #b91c1c; color: #fee2e2; }}
        .details-row td {{ background: #182234; padding: 8px 24px; }}
        .ast-list {{ margin: 0; padding-left: 18px; font-size: 13px; }}
        .ast-pass {{ color: #34d399; margin: 3px 0; }}
        .ast-fail {{ color: #f87171; margin: 3px 0; font-weight: 600; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div>
                <h1>Quantum QA Studio - Test Report</h1>
                <div style="color: #94a3b8; margin-top: 4px;">Suite: <strong>{run_result.suite_name}</strong> | Generated: {date_str}</div>
            </div>
            <div>
                <span style="font-size: 20px; font-weight: bold; color: {badge_color};">{run_result.pass_percentage}% Passed</span>
            </div>
        </div>
        <div class="stats-grid">
            <div class="stat-card"><div class="label">Total Tests</div><div class="value">{run_result.total_count}</div></div>
            <div class="stat-card"><div class="label">Passed</div><div class="value" style="color: #34d399;">{run_result.passed_count}</div></div>
            <div class="stat-card"><div class="label">Failed</div><div class="value" style="color: #f87171;">{run_result.failed_count}</div></div>
            <div class="stat-card"><div class="label">Duration</div><div class="value">{round(run_result.duration_ms, 1)}ms</div></div>
        </div>
        <table>
            <thead>
                <tr>
                    <th>#</th>
                    <th>Test Name</th>
                    <th>Method</th>
                    <th>Target URL</th>
                    <th>Status</th>
                    <th>Latency</th>
                    <th>Result</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
    </div>
</body>
</html>"""