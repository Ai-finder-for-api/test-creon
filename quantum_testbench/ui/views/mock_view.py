import customtkinter as ctk
from typing import Dict, Any
from quantum_testbench.core.mock_server import MockServerController


class MockView(ctk.CTkFrame):
    def __init__(self, master, mock_controller: MockServerController, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.mock_controller = mock_controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_top_controls()
        self._build_endpoint_registry()
        self._build_inbound_log_viewer()

    def _build_top_controls(self):
        top_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        top_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        top_frame.grid_columnconfigure(2, weight=1)

        self.toggle_btn = ctk.CTkButton(
            top_frame,
            text="Start Mock Server",
            font=("Segoe UI", 12, "bold"),
            fg_color="#10b981",
            hover_color="#059669",
            command=self._on_toggle_server
        )
        self.toggle_btn.grid(row=0, column=0, padx=12, pady=12)

        self.status_pill = ctk.CTkLabel(
            top_frame,
            text="● STOPPED",
            font=("Segoe UI", 11, "bold"),
            fg_color="#ef4444",
            text_color="#ffffff",
            corner_radius=6,
            padx=10,
            pady=4
        )
        self.status_pill.grid(row=0, column=1, padx=8, pady=12)

        info_txt = f"Host: {self.mock_controller.host}:{self.mock_controller.port} (Zero-config local sandbox)"
        ctk.CTkLabel(top_frame, text=info_txt, font=("Consolas", 11), text_color="#94a3b8").grid(row=0, column=2, sticky="w", padx=12)

        self.clear_btn = ctk.CTkButton(
            top_frame,
            text="Clear Inbound Logs",
            font=("Segoe UI", 11),
            fg_color="#334155",
            hover_color="#475569",
            command=self._on_clear_logs
        )
        self.clear_btn.grid(row=0, column=3, padx=(8, 12), pady=12)

    def _build_endpoint_registry(self):
        ep_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8, height=130)
        ep_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        ep_frame.grid_columnconfigure(0, weight=1)

        lbl = ctk.CTkLabel(ep_frame, text="REGISTERED MOCK ENDPOINTS", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        lbl.pack(anchor="w", padx=12, pady=(8, 4))

        chips_frame = ctk.CTkFrame(ep_frame, fg_color="transparent")
        chips_frame.pack(fill="x", padx=10, pady=(0, 8))

        default_eps = [
            ("GET", "/health", "200 OK (System Health)"),
            ("GET", "/api/v1/users", "200 OK (Mock User Directory)"),
            ("POST", "/api/v1/auth/login", "200 OK (JWT Token Issuer)"),
            ("GET", "/api/v1/orders/101", "200 OK (Order Details)")
        ]

        for method, path, desc in default_eps:
            chip = ctk.CTkFrame(chips_frame, fg_color="#0f172a", corner_radius=4)
            chip.pack(side="left", padx=4, pady=2)
            ctk.CTkLabel(chip, text=f"{method} {path}", font=("Consolas", 10, "bold"), text_color="#38bdf8").pack(side="left", padx=6, pady=2)
            ctk.CTkLabel(chip, text=f"• {desc}", font=("Segoe UI", 10), text_color="#94a3b8").pack(side="left", padx=(0, 6), pady=2)

    def _build_inbound_log_viewer(self):
        log_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        log_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        lbl = ctk.CTkLabel(log_frame, text="LIVE INBOUND REQUEST & WEBHOOK TRAFFIC STREAM", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self.log_textbox = ctk.CTkTextbox(log_frame, font=("Consolas", 11), fg_color="#0b1120", text_color="#f8fafc")
        self.log_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.log_textbox.insert("1.0", "Mock server is ready. Start the server to begin capturing live HTTP requests.\n")

    def _on_toggle_server(self):
        if not self.mock_controller.is_running:
            success = self.mock_controller.start(on_request=self._on_inbound_request)
            if success:
                self.toggle_btn.configure(text="Stop Mock Server", fg_color="#ef4444", hover_color="#dc2626")
                self.status_pill.configure(text="● RUNNING [127.0.0.1:8765]", fg_color="#10b981")
                self._append_log(f"[{self._now()}] Mock HTTP Server listening on http://127.0.0.1:8765\n")
        else:
            self.mock_controller.stop()
            self.toggle_btn.configure(text="Start Mock Server", fg_color="#10b981", hover_color="#059669")
            self.status_pill.configure(text="● STOPPED", fg_color="#ef4444")
            self._append_log(f"[{self._now()}] Mock HTTP Server stopped.\n")

    def _now(self):
        import time
        return time.strftime("%H:%M:%S")

    def _on_inbound_request(self, record: Dict[str, Any]):
        msg = f"[{record['timestamp']}] INBOUND {record['method']} {record['path']} from {record['client_ip']}\n"
        if record.get('body'):
            msg += f"  Payload: {record['body'][:120]}\n"
        self._append_log(msg)

    def _append_log(self, text: str):
        try:
            self.log_textbox.insert("end", text)
            self.log_textbox.see("end")
        except Exception:
            pass

    def _on_clear_logs(self):
        self.mock_controller.clear_logs() if self.mock_controller.server else None
        self.log_textbox.delete("1.0", "end")
        self.log_textbox.insert("1.0", "Inbound traffic logs cleared.\n")