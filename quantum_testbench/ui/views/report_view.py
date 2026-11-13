import customtkinter as ctk
from typing import Optional
from quantum_testbench.models.data_models import SuiteRunResult
from quantum_testbench.core.reporter import ReportGenerator


class ReportView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.current_report: Optional[SuiteRunResult] = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_report_body()

    def set_report(self, report: SuiteRunResult):
        self.current_report = report
        self.status_lbl.configure(
            text=f"Loaded: {report.suite_name} ({report.pass_percentage}% Passed)",
            text_color="#34d399" if report.failed_count == 0 else "#f87171"
        )
        self._update_display()

    def _build_header(self):
        h_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        h_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        h_frame.grid_columnconfigure(0, weight=1)

        self.status_lbl = ctk.CTkLabel(
            h_frame,
            text="No test report loaded yet. Run a test suite to view and export reports.",
            font=("Segoe UI", 12, "bold"),
            text_color="#94a3b8"
        )
        self.status_lbl.grid(row=0, column=0, sticky="w", padx=14, pady=10)

        self.fmt_var = ctk.StringVar(value="Markdown")
        self.fmt_menu = ctk.CTkSegmentedButton(
            h_frame,
            values=["Markdown", "JSON", "HTML Source"],
            variable=self.fmt_var,
            command=lambda _: self._update_display()
        )
        self.fmt_menu.grid(row=0, column=1, padx=8, pady=10)

        self.save_btn = ctk.CTkButton(
            h_frame,
            text="💾 Save to /tmp/qa_report",
            font=("Segoe UI", 11, "bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self._on_save
        )
        self.save_btn.grid(row=0, column=2, padx=(8, 12), pady=10)

    def _build_report_body(self):
        b_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        b_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        b_frame.grid_columnconfigure(0, weight=1)
        b_frame.grid_rowconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(b_frame, font=("Consolas", 12), fg_color="#0b1120", text_color="#f8fafc")
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.textbox.insert("1.0", "# Quantum QA Test Report Viewer\n\nRun a suite in the 'Test Suites' tab to generate a detailed report.\n")

    def _update_display(self):
        if not self.current_report:
            return
        fmt = self.fmt_var.get()
        if fmt == "Markdown":
            content = ReportGenerator.to_markdown(self.current_report)
        elif fmt == "JSON":
            content = ReportGenerator.to_json(self.current_report)
        else:
            content = ReportGenerator.to_html(self.current_report)

        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", content)

    def _on_save(self):
        if not self.current_report:
            return
        fmt = self.fmt_var.get()
        ext = "md" if fmt == "Markdown" else ("json" if fmt == "JSON" else "html")
        path = f"/tmp/quantum_qa_report.{ext}"
        content = self.textbox.get("1.0", "end").strip()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        self.save_btn.configure(text=f"✓ Saved ({ext.upper()})")