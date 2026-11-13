import json
import customtkinter as ctk
from typing import Optional
from quantum_testbench.models.data_models import (
    RequestDefinition, HttpMethod, Assertion, AssertionType
)
from quantum_testbench.core.client import HttpClient


class ApiView(ctk.CTkFrame):
    def __init__(self, master, http_client: HttpClient, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.http_client = http_client

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_bar()
        self._build_request_panel()
        self._build_response_panel()

    def _build_top_bar(self):
        top_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8, height=60)
        top_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 10))
        top_frame.grid_columnconfigure(1, weight=1)

        self.method_var = ctk.StringVar(value="GET")
        self.method_menu = ctk.CTkOptionMenu(
            top_frame,
            values=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD"],
            variable=self.method_var,
            width=100,
            fg_color="#0284c7",
            button_color="#0369a1",
            font=("Segoe UI", 13, "bold")
        )
        self.method_menu.grid(row=0, column=0, padx=(12, 8), pady=12)

        self.url_entry = ctk.CTkEntry(
            top_frame,
            placeholder_text="Enter target URL or {{BASE_URL}}/api/v1/users",
            font=("Consolas", 13),
            fg_color="#0f172a",
            border_color="#334155"
        )
        self.url_entry.insert(0, "{{BASE_URL}}/api/v1/users")
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=12)

        self.send_btn = ctk.CTkButton(
            top_frame,
            text="Send Request 🚀",
            font=("Segoe UI", 13, "bold"),
            fg_color="#10b981",
            hover_color="#059669",
            width=130,
            command=self._on_send_click
        )
        self.send_btn.grid(row=0, column=2, padx=(8, 12), pady=12)

    def _build_request_panel(self):
        req_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        req_frame.grid(row=1, column=0, sticky="nsew", padx=(10, 5), pady=0)
        req_frame.grid_columnconfigure(0, weight=1)
        req_frame.grid_rowconfigure(1, weight=1)

        lbl = ctk.CTkLabel(req_frame, text="REQUEST CONFIGURATION", font=("Segoe UI", 12, "bold"), text_color="#94a3b8")
        lbl.grid(row=0, column=0, sticky="w", padx=14, pady=(10, 4))

        self.req_tabview = ctk.CTkTabview(req_frame, fg_color="#0f172a")
        self.req_tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        tab_body = self.req_tabview.add("Body (JSON)")
        tab_headers = self.req_tabview.add("Headers")
        tab_ast = self.req_tabview.add("QA Assertions")

        # Body Tab
        tab_body.grid_columnconfigure(0, weight=1)
        tab_body.grid_rowconfigure(0, weight=1)
        self.body_textbox = ctk.CTkTextbox(tab_body, font=("Consolas", 12), fg_color="#0b1120")
        initial_body = '{\n  "query": "all_active",\n  "page": 1\n}'
        self.body_textbox.insert("1.0", initial_body)
        self.body_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Headers Tab
        tab_headers.grid_columnconfigure(0, weight=1)
        tab_headers.grid_rowconfigure(0, weight=1)
        self.headers_textbox = ctk.CTkTextbox(tab_headers, font=("Consolas", 12), fg_color="#0b1120")
        initial_headers = "Content-Type: application/json\nAuthorization: Bearer {{API_KEY}}\nX-Client-ID: quantum-qa-bench"
        self.headers_textbox.insert("1.0", initial_headers)
        self.headers_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # QA Assertions Tab
        tab_ast.grid_columnconfigure(0, weight=1)
        tab_ast.grid_rowconfigure(1, weight=1)
        ast_hint = ctk.CTkLabel(
            tab_ast,
            text="Configure automated validation checks (1 per line):\nFormat: STATUS:200 | LATENCY:500 | CONTAINS:text | JSON:key.path:expected",
            font=("Segoe UI", 11),
            text_color="#94a3b8",
            justify="left"
        )
        ast_hint.grid(row=0, column=0, sticky="w", padx=5, pady=(2, 6))

        self.assertions_textbox = ctk.CTkTextbox(tab_ast, font=("Consolas", 12), fg_color="#0b1120")
        initial_ast = "STATUS:200\nLATENCY:500\nCONTAINS:Alice\nHEADER:content-type"
        self.assertions_textbox.insert("1.0", initial_ast)
        self.assertions_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

    def _build_response_panel(self):
        resp_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        resp_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 10), pady=0)
        resp_frame.grid_columnconfigure(0, weight=1)
        resp_frame.grid_rowconfigure(1, weight=1)

        header_bar = ctk.CTkFrame(resp_frame, fg_color="transparent")
        header_bar.grid(row=0, column=0, sticky="ew", padx=14, pady=(10, 4))
        header_bar.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(header_bar, text="INSPECTION RESPONSE", font=("Segoe UI", 12, "bold"), text_color="#94a3b8")
        lbl.grid(row=0, column=0, sticky="w")

        self.status_pill = ctk.CTkLabel(
            header_bar,
            text="NO REQUEST SENT",
            font=("Segoe UI", 11, "bold"),
            fg_color="#334155",
            text_color="#e2e8f0",
            corner_radius=6,
            padx=10,
            pady=2
        )
        self.status_pill.grid(row=0, column=1, padx=4)

        self.time_pill = ctk.CTkLabel(
            header_bar,
            text="0 ms",
            font=("Segoe UI", 11, "bold"),
            fg_color="#334155",
            text_color="#38bdf8",
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.time_pill.grid(row=0, column=2, padx=4)

        self.resp_tabview = ctk.CTkTabview(resp_frame, fg_color="#0f172a")
        self.resp_tabview.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        tab_body = self.resp_tabview.add("Response Body")
        tab_ast_res = self.resp_tabview.add("Assertion Verdicts")
        tab_headers = self.resp_tabview.add("Response Headers")

        # Response Body Tab
        tab_body.grid_columnconfigure(0, weight=1)
        tab_body.grid_rowconfigure(0, weight=1)
        self.resp_body_textbox = ctk.CTkTextbox(tab_body, font=("Consolas", 12), fg_color="#0b1120")
        self.resp_body_textbox.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Assertion Verdicts Tab
        tab_ast_res.grid_columnconfigure(0, weight=1)
        tab_ast_res.grid_rowconfigure(0, weight=1)
        self.ast_verdicts_box = ctk.CTkTextbox(tab_ast_res, font=("Consolas", 12), fg_color="#0b1120")
        self.ast_verdicts_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Response Headers Tab
        tab_headers.grid_columnconfigure(0, weight=1)
        tab_headers.grid_rowconfigure(0, weight=1)
        self.resp_headers_box = ctk.CTkTextbox(tab_headers, font=("Consolas", 12), fg_color="#0b1120")
        self.resp_headers_box.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

    def _parse_headers(self) -> dict:
        headers = {}
        raw = self.headers_textbox.get("1.0", "end").strip()
        for line in raw.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()
        return headers

    def _parse_assertions(self) -> list:
        assertions = []
        raw = self.assertions_textbox.get("1.0", "end").strip()
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                atype, val = line.split(":", 1)
                atype = atype.strip().upper()
                val = val.strip()
                if atype == "STATUS":
                    assertions.append(Assertion(AssertionType.STATUS_EQUALS, int(val)))
                elif atype == "LATENCY":
                    assertions.append(Assertion(AssertionType.LATENCY_LESS_THAN, float(val)))
                elif atype == "CONTAINS":
                    assertions.append(Assertion(AssertionType.BODY_CONTAINS, val))
                elif atype == "HEADER":
                    assertions.append(Assertion(AssertionType.HEADER_EXISTS, val))
                elif atype == "JSON":
                    assertions.append(Assertion(AssertionType.JSON_PATH_EQUALS, val))
        return assertions

    def _on_send_click(self):
        method_str = self.method_var.get()
        method_enum = HttpMethod(method_str)
        url = self.url_entry.get().strip()
        headers = self._parse_headers()
        body = self.body_textbox.get("1.0", "end").strip()
        assertions = self._parse_assertions()

        req_def = RequestDefinition(
            id="req_manual",
            name="Manual Request",
            method=method_enum,
            url=url,
            headers=headers,
            body=body if method_str in ("POST", "PUT", "PATCH") else None,
            assertions=assertions
        )

        self.send_btn.configure(state="disabled", text="Sending...")
        self.update()

        try:
            result = self.http_client.execute(req_def)
            self._render_result(result)
        finally:
            self.send_btn.configure(state="normal", text="Send Request 🚀")

    def _render_result(self, result):
        resp = result.response
        if not resp:
            self.status_pill.configure(text="ERROR", fg_color="#ef4444")
            self.time_pill.configure(text="-")
            self.resp_body_textbox.delete("1.0", "end")
            self.resp_body_textbox.insert("1.0", f"Error: {result.error}")
            return

        if 200 <= resp.status_code < 300:
            pill_color = "#10b981"
        elif 300 <= resp.status_code < 400:
            pill_color = "#f59e0b"
        else:
            pill_color = "#ef4444"

        self.status_pill.configure(text=f"{resp.status_code} {resp.status_text}", fg_color=pill_color)
        self.time_pill.configure(text=f"{round(resp.elapsed_ms, 1)} ms")

        self.resp_body_textbox.delete("1.0", "end")
        try:
            parsed = json.loads(resp.body)
            pretty = json.dumps(parsed, indent=2)
            self.resp_body_textbox.insert("1.0", pretty)
        except Exception:
            self.resp_body_textbox.insert("1.0", resp.body)

        self.resp_headers_box.delete("1.0", "end")
        h_lines = [f"{k}: {v}" for k, v in resp.headers.items()]
        self.resp_headers_box.insert("1.0", "\n".join(h_lines))

        self.ast_verdicts_box.delete("1.0", "end")
        if result.assertion_results:
            lines = []
            for ast in result.assertion_results:
                badge = "[PASSED ✓]" if ast.passed else "[FAILED ✗]"
                lines.append(f"{badge} {ast.message}")
            overall = "OVERALL VERDICT: PASSED" if result.passed else "OVERALL VERDICT: FAILED"
            self.ast_verdicts_box.insert("1.0", f"{overall}\n{'='*35}\n" + "\n".join(lines))
        else:
            verdict = "PASSED" if result.passed else "FAILED"
            self.ast_verdicts_box.insert("1.0", f"No explicit assertions configured.\nHTTP Status Evaluation: {verdict}")