import customtkinter as ctk
from quantum_testbench.core.environment import EnvironmentManager


class EnvView(ctk.CTkFrame):
    def __init__(self, master, env_manager: EnvironmentManager, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.env_manager = env_manager

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_top_controls()
        self._build_vars_list()

    def _build_top_controls(self):
        c_frame = ctk.CTkFrame(self, fg_color="#1e293b", corner_radius=8)
        c_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        c_frame.grid_columnconfigure(1, weight=1)
        c_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(c_frame, text="Key:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8").grid(row=0, column=0, padx=(12, 4), pady=10)
        self.key_entry = ctk.CTkEntry(c_frame, placeholder_text="e.g. AUTH_TOKEN", font=("Consolas", 11), fg_color="#0f172a")
        self.key_entry.grid(row=0, column=1, sticky="ew", padx=4, pady=10)

        ctk.CTkLabel(c_frame, text="Value:", font=("Segoe UI", 11, "bold"), text_color="#94a3b8").grid(row=0, column=2, padx=(12, 4), pady=10)
        self.val_entry = ctk.CTkEntry(c_frame, placeholder_text="e.g. secret_token_value", font=("Consolas", 11), fg_color="#0f172a")
        self.val_entry.grid(row=0, column=3, sticky="ew", padx=4, pady=10)

        self.add_btn = ctk.CTkButton(
            c_frame,
            text="+ Add / Update",
            font=("Segoe UI", 11, "bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            command=self._on_add_var
        )
        self.add_btn.grid(row=0, column=4, padx=(8, 12), pady=10)

    def _build_vars_list(self):
        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="#1e293b", corner_radius=8)
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=0)
        self.scroll_frame.grid_columnconfigure(1, weight=1)
        self._refresh_vars()

    def _refresh_vars(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        vars_dict = self.env_manager.get_all()
        for idx, (k, v) in enumerate(vars_dict.items()):
            row = ctk.CTkFrame(self.scroll_frame, fg_color="#0f172a", corner_radius=6)
            row.pack(fill="x", padx=6, pady=4)
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(row, text=f"{{{{{k}}}}}", font=("Consolas", 12, "bold"), text_color="#38bdf8", width=160, anchor="w").grid(row=0, column=0, padx=12, pady=8)
            ctk.CTkLabel(row, text=str(v), font=("Consolas", 11), text_color="#f8fafc", anchor="w").grid(row=0, column=1, sticky="ew", padx=8, pady=8)

            del_btn = ctk.CTkButton(
                row,
                text="✕",
                width=32,
                height=26,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda key=k: self._on_delete_var(key)
            )
            del_btn.grid(row=0, column=2, padx=10, pady=8)

    def _on_add_var(self):
        k = self.key_entry.get().strip()
        v = self.val_entry.get().strip()
        if k:
            self.env_manager.set(k, v)
            self.key_entry.delete(0, "end")
            self.val_entry.delete(0, "end")
            self._refresh_vars()

    def _on_delete_var(self, key):
        self.env_manager.remove(key)
        self._refresh_vars()