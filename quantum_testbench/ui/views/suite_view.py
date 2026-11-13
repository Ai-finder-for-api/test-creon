import time
import customtkinter as ctk
from typing import Dict, List, Optional
from quantum_testbench.models.data_models import (
    TestSuite, RequestDefinition, HttpMethod, Assertion, AssertionType, SuiteRunResult
)
from quantum_testbench.core.runner import SuiteRunner
from quantum_testbench.core.reporter import ReportGenerator


class SuiteView(ctk.CTkFrame):
    def __init__(self, master, suite_runner: SuiteRunner, on_suite_completed=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.suite_runner = suite_runner
        self.on_suite_completed = on_suite_completed
        self.suites: Dict[str, TestSuite] = self._load_default_suites()
        self.last_run_result: Optional[SuiteRunResult] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_controls()
        self._build_metrics_bar()
        self._build_results_table()

    def _load_default_suites(self) -> Dict[str, TestSuite]:
        s1 = TestSuite(
            id="suite_health",
            name="1. Health & Core Readiness Suite",
            description="Validates uptime, readiness probes, and core ping latency",
            requests=[
                RequestDefinition(
                    id="req_h1",
                    name="Ping Health Probe",
                    method=HttpMethod.GET,
                    url="{{BASE_URL}}/health",
                    assertions=[
                        Assertion(AssertionType.STATUS_EQUALS, 200),
                        Assertion(AssertionType.LATENCY_LESS_THAN, 200.0),
                        Assertion(AssertionType.JSON_PATH_EQUALS, "status:healthy")
                    ]
                ),
                RequestDefinition(
                    id="req_h2",
                    name="Verify Response Header",
                    method=HttpMethod.GET,
                    url="{{BASE_URL}}/health",
                    assertions=[
                        Assertion(AssertionType.STATUS_EQUALS, 200),
                        Assertion(AssertionType.HEADER_EXISTS, "server")
                    ]
                )
            ]
        )

        s2 = TestSuite(
            id="suite_users",
            name="2. User Management & Auth Suite",
            description="End-to-end authentication and user account operations",
            requests=[
                RequestDefinition(
                    id="req_u1",
                    name="User Authentication Login",
                    method=HttpMethod.POST,
                    url="{{BASE_URL}}/api/v1/auth/login",
                    headers={"Content-Type": "application/json"},
                    body='{"username": "qa_tester", "password": "secure_password"}',
                    assertions=[
                        Assertion(AssertionType.STATUS_EQUALS, 200),
                        Assertion(AssertionType.BODY_CONTAINS, "token"),
                        Assertion(AssertionType.LATENCY_LESS_THAN, 300.0)
                    ]
                ),
                RequestDefinition(
                    id="req_u2",
                    name="List Active Users",
                    method=HttpMethod.GET,
                    url="{{BASE_URL}}/api/v1/users",
                    assertions=[
                        Assertion(AssertionType.STATUS_EQUALS, 200),
                        Assertion(AssertionType.BODY_CONTAINS, "Alice Vance")
                    ]
                )
            ]
        )

        s3 = TestSuite(
            id="suite_full",
            name="3. Complete System Regression Test",
            description="Runs all end-to-end integration assertions across all endpoints",
            requests=s1.requests + s2.requests + [
                RequestDefinition(
                    id="req_ord",
                    name="Fetch Verified Order Details",
                    method=HttpMethod.GET,
                    url="{{BASE_URL}}/api/v1/orders/101",
                    assertions=[
                        Assertion(AssertionType.STATUS_EQUALS, 200),
                        Assertion(AssertionType.JSON_PATH_EQUALS, "status:COMPLETED"),
                        Assertion(AssertionType.BODY_CONTAINS, "USD")
                    ]
                )
            ]
        )

        return {s1.id: s1, s2.id: s2, s3.id: s3}

    def _build_controls(self):
        ctrl_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        ctrl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        ctrl_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(ctrl_frame, text="Select Suite:", font=("Segoe UI", 12, "bold"), text_color="#94a3b8").grid(row=0, column=0, padx=12, pady=12)

        suite_names = [s.name for s in self.suites.values()]
        self.suite_var = ctk.StringVar(value=suite_names[0])
        self.suite_menu = ctk.CTkOptionMenu(
            ctrl_frame,
            values=suite_names,
            variable=self.suite_var,
            width=320,
            fg_color="#0f172a",
            button_color="#334155"
        )
        self.suite_menu.grid(row=0, column=1, sticky="w", padx=8, pady=12)

        self.run_btn = ctk.CTkButton(
            ctrl_frame,
            text="▶ Run Entire Suite",
            font=("Segoe UI", 13, "bold"),
            fg_color="#3b82f6",
            hover_color="#2563eb",
            command=self._on_run_suite
        )
        self.run_btn.grid(row=0, column=2, padx=8, pady=12)

        self.export_btn = ctk.CTkButton(
            ctrl_frame,
            text="📥 Export Report",
            font=("Segoe UI", 12, "bold"),
            fg_color="#334155",
            hover_color="#475569",
            command=self._on_export_report
        )
        self.export_btn.grid(row=0, column=3, padx=(8, 12), pady=12)

    def _build_metrics_bar(self):
        m_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        m_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        m_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.total_card = self._create_metric_box(m_frame, 0, "TOTAL TESTS", "0")
        self.passed_card = self._create_metric_box(m_frame, 1, "PASSED", "0", color="#34d399")
        self.failed_card = self._create_metric_box(m_frame, 2, "FAILED", "0", color="#f87171")
        self.rate_card = self._create_metric_box(m_frame, 3, "PASS RATE", "100%", color="#38bdf8")

    def _create_metric_box(self, parent, col, title, initial_val, color="#ffffff"):
        box = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=6)
        box.grid(row=0, column=col, padx=8, pady=8, sticky="ew")
        lbl_title = ctk.CTkLabel(box, text=title, font=("Segoe UI", 10, "bold"), text_color="#94a3b8")
        lbl_title.pack(anchor="w", padx=10, pady=(6, 2))
        lbl_val = ctk.CTkLabel(box, text=initial_val, font=("Segoe UI", 20, "bold"), text_color=color)
        lbl_val.pack(anchor="w", padx=10, pady=(0, 6))
        return lbl_val

    def _build_results_table(self):
        self.results_frame = ctk.CTkScrollableFrame(self, fg_color="#1e293b", corner_radius=8)
        self.results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)
        self.results_frame.grid_columnconfigure(0, weight=1)

        empty_label = ctk.CTkLabel(
            self.results_frame,
            text="No test suite executed yet. Choose a suite above and click 'Run Entire Suite'.",
            font=("Segoe UI", 13),
            text_color="#94a3b8"
        )
        empty_label.pack(pady=40)

    def _on_run_suite(self):
        selected_name = self.suite_var.get()
        suite = next((s for s in self.suites.values() if s.name == selected_name), None)
        if not suite:
            return

        self.run_btn.configure(state="disabled", text="Running...")
        self.update()

        # Clear previous items
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        try:
            run_result = self.suite_runner.run_suite(suite)
            self.last_run_result = run_result

            # Update metrics
            self.total_card.configure(text=str(run_result.total_count))
            self.passed_card.configure(text=str(run_result.passed_count))
            self.failed_card.configure(text=str(run_result.failed_count))
            self.rate_card.configure(text=f"{run_result.pass_percentage}%")

            # Render item cards
            for res in run_result.results:
                self._render_test_card(res)

            if self.on_suite_completed:
                self.on_suite_completed(run_result)

        finally:
            self.run_btn.configure(state="normal", text="▶ Run Entire Suite")

    def _render_test_card(self, test_result):
        req = test_result.request
        resp = test_result.response

        card = ctk.CTkFrame(self.results_frame, fg_color="#0f172a", corner_radius=6, border_width=1, border_color="#334155")
        card.pack(fill="x", padx=6, pady=4)
        card.grid_columnconfigure(1, weight=1)

        # Method badge
        m_colors = {"GET": "#0284c7", "POST": "#059669", "PUT": "#d97706", "DELETE": "#dc2626"}
        m_bg = m_colors.get(req.method.value, "#475569")
        m_lbl = ctk.CTkLabel(card, text=req.method.value, font=("Consolas", 11, "bold"), fg_color=m_bg, text_color="#ffffff", corner_radius=4, width=54)
        m_lbl.grid(row=0, column=0, padx=10, pady=8)

        # Test name & URL
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", padx=6, pady=6)
        name_lbl = ctk.CTkLabel(info_frame, text=req.name, font=("Segoe UI", 12, "bold"), text_color="#f8fafc")
        name_lbl.pack(anchor="w")
        url_lbl = ctk.CTkLabel(info_frame, text=req.url, font=("Consolas", 11), text_color="#94a3b8")
        url_lbl.pack(anchor="w")

        # Latency & Status
        meta_frame = ctk.CTkFrame(card, fg_color="transparent")
        meta_frame.grid(row=0, column=2, padx=10, pady=6)
        if resp:
            ctk.CTkLabel(meta_frame, text=f"{round(resp.elapsed_ms, 1)} ms", font=("Consolas", 11), text_color="#38bdf8").pack(anchor="e")
            ctk.CTkLabel(meta_frame, text=f"HTTP {resp.status_code}", font=("Consolas", 10), text_color="#94a3b8").pack(anchor="e")

        # Verdict Badge
        v_bg = "#059669" if test_result.passed else "#dc2626"
        v_text = "PASSED" if test_result.passed else "FAILED"
        v_lbl = ctk.CTkLabel(card, text=v_text, font=("Segoe UI", 11, "bold"), fg_color=v_bg, text_color="#ffffff", corner_radius=4, width=70)
        v_lbl.grid(row=0, column=3, padx=(6, 12), pady=8)

        # Assertions list
        if test_result.assertion_results:
            ast_frame = ctk.CTkFrame(card, fg_color="#080e1a", corner_radius=4)
            ast_frame.grid(row=1, column=0, columnspan=4, sticky="ew", padx=8, pady=(0, 6))
            for a in test_result.assertion_results:
                icon = "✓" if a.passed else "✗"
                a_color = "#34d399" if a.passed else "#f87171"
                row_txt = f"  [{icon}] {a.message}"
                ctk.CTkLabel(ast_frame, text=row_txt, font=("Consolas", 10), text_color=a_color).pack(anchor="w", padx=6, pady=1)

    def _on_export_report(self):
        if not self.last_run_result:
            return
        # Save HTML report to /tmp/qa_report.html
        html = ReportGenerator.to_html(self.last_run_result)
        with open("/tmp/quantum_qa_report.html", "w", encoding="utf-8") as f:
            f.write(html)
        self.export_btn.configure(text="✓ Exported to /tmp/quantum_qa_report.html")