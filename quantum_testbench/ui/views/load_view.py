import customtkinter as ctk
from quantum_testbench.models.data_models import LoadTestConfig, HttpMethod
from quantum_testbench.core.load_tester import LoadTestRunner


class LoadView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.runner = LoadTestRunner()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_config_panel()
        self._build_metrics_panel()
        self._build_distribution_panel()

    def _build_config_panel(self):
        c_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        c_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        c_frame.grid_columnconfigure(1, weight=1)

        # URL
        ctk.CTkLabel(c_frame, text="Target URL:", font=("Segoe UI", 12, "bold"), text_color="#94a3b8").grid(row=0, column=0, padx=12, pady=10)
        self.url_entry = ctk.CTkEntry(c_frame, font=("Consolas", 12), fg_color="#0f172a", border_color="#334155")
        self.url_entry.insert(0, "http://127.0.0.1:8765/health")
        self.url_entry.grid(row=0, column=1, sticky="ew", padx=8, pady=10)

        # Concurrency & Total
        settings_frame = ctk.CTkFrame(c_frame, fg_color="transparent")
        settings_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 10))

        ctk.CTkLabel(settings_frame, text="Concurrency:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8").pack(side="left", padx=(0, 6))
        self.concurrency_slider = ctk.CTkSlider(settings_frame, from_=1, to=30, number_of_steps=29, width=120)
        self.concurrency_slider.set(8)
        self.concurrency_slider.pack(side="left", padx=4)

        self.concurrency_lbl = ctk.CTkLabel(settings_frame, text="8 workers", font=("Consolas", 11), text_color="#38bdf8")
        self.concurrency_lbl.pack(side="left", padx=(4, 18))
        self.concurrency_slider.configure(command=lambda val: self.concurrency_lbl.configure(text=f"{int(val)} workers"))

        ctk.CTkLabel(settings_frame, text="Total Requests:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8").pack(side="left", padx=(0, 6))
        self.requests_slider = ctk.CTkSlider(settings_frame, from_=10, to=200, number_of_steps=19, width=120)
        self.requests_slider.set(50)
        self.requests_slider.pack(side="left", padx=4)

        self.requests_lbl = ctk.CTkLabel(settings_frame, text="50 reqs", font=("Consolas", 11), text_color="#38bdf8")
        self.requests_lbl.pack(side="left", padx=(4, 18))
        self.requests_slider.configure(command=lambda val: self.requests_lbl.configure(text=f"{int(val)} reqs"))

        self.run_btn = ctk.CTkButton(
            settings_frame,
            text="⚡ Run Load Benchmark",
            font=("Segoe UI", 12, "bold"),
            fg_color="#f59e0b",
            hover_color="#d97706",
            command=self._on_run_load
        )
        self.run_btn.pack(side="right", padx=6)

    def _build_metrics_panel(self):
        m_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        m_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        m_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.card_rps = self._create_card(m_frame, 0, "THROUGHPUT", "0.0 RPS", "#38bdf8")
        self.card_avg = self._create_card(m_frame, 1, "AVG LATENCY", "0.0 ms", "#34d399")
        self.card_p95 = self._create_card(m_frame, 2, "P95 LATENCY", "0.0 ms", "#f59e0b")
        self.card_success = self._create_card(m_frame, 3, "SUCCESS RATE", "100%", "#10b981")

    def _create_card(self, parent, col, title, initial_val, color):
        box = ctk.CTkFrame(parent, fg_color="#0f172a", corner_radius=6)
        box.grid(row=0, column=col, padx=8, pady=8, sticky="ew")
        lbl_t = ctk.CTkLabel(box, text=title, font=("Segoe UI", 10, "bold"), text_color="#94a3b8")
        lbl_t.pack(anchor="w", padx=10, pady=(6, 2))
        lbl_v = ctk.CTkLabel(box, text=initial_val, font=("Segoe UI", 18, "bold"), text_color=color)
        lbl_v.pack(anchor="w", padx=10, pady=(0, 6))
        return lbl_v

    def _build_distribution_panel(self):
        d_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        d_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=0)
        d_frame.grid_columnconfigure(0, weight=1)
        d_frame.grid_rowconfigure(1, weight=1)

        lbl = ctk.CTkLabel(d_frame, text="LATENCY PERCENTILES & EXECUTION BREAKDOWN", font=("Segoe UI", 11, "bold"), text_color="#94a3b8")
        lbl.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 4))

        self.details_box = ctk.CTkTextbox(d_frame, font=("Consolas", 12), fg_color="#0b1120", text_color="#f8fafc")
        self.details_box.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.details_box.insert("1.0", "Configure your benchmark parameters above and click 'Run Load Benchmark'.\n")

    def _on_run_load(self):
        url = self.url_entry.get().strip()
        concurrency = int(self.concurrency_slider.get())
        total = int(self.requests_slider.get())

        config = LoadTestConfig(
            url=url,
            method=HttpMethod.GET,
            concurrency=concurrency,
            total_requests=total
        )

        self.run_btn.configure(state="disabled", text="Running Load...")
        self.update()

        try:
            result = self.runner.run(config)
            self.card_rps.configure(text=f"{result.rps} RPS")
            self.card_avg.configure(text=f"{result.avg_latency_ms} ms")
            self.card_p95.configure(text=f"{result.p95_ms} ms")

            succ_rate = round((result.successful_requests / result.total_requests) * 100, 1) if result.total_requests > 0 else 0
            self.card_success.configure(text=f"{succ_rate}%")

            text = (
                f"LOAD TEST COMPLETED SUCCESSFULLY\n"
                f"{'=' * 50}\n"
                f"Target Endpoint:       {config.url}\n"
                f"Total Requests:        {result.total_requests}\n"
                f"Concurrent Workers:    {config.concurrency}\n"
                f"Total Wall Clock Time: {result.total_duration_sec} seconds\n"
                f"Throughput (RPS):      {result.rps} req/sec\n\n"
                f"LATENCY PERCENTILE DISTRIBUTION:\n"
                f"  Min Latency:         {result.min_latency_ms} ms\n"
                f"  Median (p50):        {result.p50_ms} ms\n"
                f"  p90:                 {result.p90_ms} ms\n"
                f"  p95:                 {result.p95_ms} ms\n"
                f"  p99:                 {result.p99_ms} ms\n"
                f"  Max Latency:         {result.max_latency_ms} ms\n"
                f"  Mean Latency:        {result.avg_latency_ms} ms\n\n"
                f"STATUS CODES:\n"
            )
            for code, count in result.status_distribution.items():
                text += f"  HTTP {code}: {count} responses\n"

            self.details_box.delete("1.0", "end")
            self.details_box.insert("1.0", text)
        finally:
            self.run_btn.configure(state="normal", text="⚡ Run Load Benchmark")