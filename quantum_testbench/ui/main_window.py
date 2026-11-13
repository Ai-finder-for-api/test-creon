import customtkinter as ctk
from quantum_testbench.core.environment import EnvironmentManager
from quantum_testbench.core.client import HttpClient
from quantum_testbench.core.runner import SuiteRunner
from quantum_testbench.core.mock_server import MockServerController
from quantum_testbench.ui.views.api_view import ApiView
from quantum_testbench.ui.views.suite_view import SuiteView
from quantum_testbench.ui.views.mock_view import MockView
from quantum_testbench.ui.views.load_view import LoadView
from quantum_testbench.ui.views.env_view import EnvView
from quantum_testbench.ui.views.report_view import ReportView


class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Appearance & Configuration
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Quantum TestBench — Professional QA & API Studio")
        self.geometry("1180x750")
        self.minsize(980, 620)

        # Core Services
        self.env_manager = EnvironmentManager()
        self.http_client = HttpClient(env_manager=self.env_manager)
        self.suite_runner = SuiteRunner(http_client=self.http_client, env_manager=self.env_manager)
        self.mock_controller = MockServerController(host="127.0.0.1", port=8765)

        # Auto-start mock server for zero-friction local testing
        self.mock_controller.start()

        # Layout Setup: Left Sidebar (width=220) + Right Content Frame
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()
        self._build_sidebar()
        self._build_content_area()
        self._build_status_bar()

        # Show default view
        self._select_view("api")

        # Cleanup on close
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(self, height=54, fg_color="#090d16", corner_radius=0)
        self.header_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        # Brand / Logo
        brand_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        brand_frame.grid(row=0, column=0, padx=16, pady=8, sticky="w")

        logo_lbl = ctk.CTkLabel(brand_frame, text="⚡ QUANTUM TESTBENCH", font=("Segoe UI", 16, "bold"), text_color="#38bdf8")
        logo_lbl.pack(side="left")

        ver_pill = ctk.CTkLabel(brand_frame, text="v1.0.0 QA-STUDIO", font=("Segoe UI", 10, "bold"), fg_color="#1e293b", text_color="#94a3b8", corner_radius=4, padx=6, pady=2)
        ver_pill.pack(side="left", padx=8)

        # Environment & Quick Status
        right_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_frame.grid(row=0, column=2, padx=16, pady=8, sticky="e")

        self.mock_badge = ctk.CTkLabel(
            right_frame,
            text="● Mock Server: Active (127.0.0.1:8765)",
            font=("Segoe UI", 11, "bold"),
            text_color="#34d399",
            fg_color="#064e3b",
            corner_radius=6,
            padx=10,
            pady=3
        )
        self.mock_badge.pack(side="right", padx=6)

    def _build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, fg_color="#0f172a", corner_radius=0)
        self.sidebar_frame.grid(row=1, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        lbl = ctk.CTkLabel(self.sidebar_frame, text="NAVIGATION", font=("Segoe UI", 10, "bold"), text_color="#64748b")
        lbl.pack(anchor="w", padx=16, pady=(16, 8))

        self.nav_buttons = {}
        items = [
            ("api", "🚀  API Tester"),
            ("suites", "📋  Test Suites"),
            ("load", "⚡  Load Bench"),
            ("mock", "📡  Mock Server & Logs"),
            ("env", "🌐  Environments"),
            ("reports", "📊  Test Reports")
        ]

        for key, text in items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                font=("Segoe UI", 12, "bold"),
                anchor="w",
                height=38,
                fg_color="transparent",
                hover_color="#1e293b",
                text_color="#cbd5e1",
                corner_radius=6,
                command=lambda k=key: self._select_view(k)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

    def _build_content_area(self):
        self.content_container = ctk.CTkFrame(self, fg_color="#0b0f19", corner_radius=0)
        self.content_container.grid(row=1, column=1, sticky="nsew", padx=8, pady=8)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # Initialize Views
        self.views = {
            "api": ApiView(self.content_container, http_client=self.http_client),
            "suites": SuiteView(self.content_container, suite_runner=self.suite_runner, on_suite_completed=self._on_suite_run_finished),
            "load": LoadView(self.content_container),
            "mock": MockView(self.content_container, mock_controller=self.mock_controller),
            "env": EnvView(self.content_container, env_manager=self.env_manager),
            "reports": ReportView(self.content_container)
        }

    def _build_status_bar(self):
        self.status_bar = ctk.CTkFrame(self, height=26, fg_color="#090d16", corner_radius=0)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.status_bar.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.status_bar,
            text="Quantum QA Studio | Engine: Native CPython + Async Mock Server | High-DPI Enabled",
            font=("Segoe UI", 10),
            text_color="#64748b"
        ).grid(row=0, column=0, padx=12, sticky="w")

        ctk.CTkLabel(
            self.status_bar,
            text="Active Environment: Local Sandbox (Mock)",
            font=("Segoe UI", 10, "bold"),
            text_color="#38bdf8"
        ).grid(row=0, column=2, padx=12, sticky="e")

    def _select_view(self, view_key: str):
        # Update button visual states
        for k, btn in self.nav_buttons.items():
            if k == view_key:
                btn.configure(fg_color="#1e293b", text_color="#38bdf8")
            else:
                btn.configure(fg_color="transparent", text_color="#cbd5e1")

        # Switch view
        for k, view in self.views.items():
            if k == view_key:
                view.grid(row=0, column=0, sticky="nsew")
            else:
                view.grid_forget()

    def _on_suite_run_finished(self, run_result):
        # Propagate report to report view
        self.views["reports"].set_report(run_result)

    def _on_close(self):
        if self.mock_controller.is_running:
            self.mock_controller.stop()
        self.destroy()