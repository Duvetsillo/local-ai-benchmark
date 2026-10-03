"""Task-oriented desktop layouts; all measurements come from local data."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .theme import COLORS, FONTS


class StudioWorkspaceMixin:
    def create_top_navigation(self, parent: tk.Widget) -> None:
        bar = tk.Frame(parent, bg=COLORS["shell"])
        bar.pack(fill="x", pady=(0, 20))
        top = tk.Frame(bar, bg=COLORS["shell"])
        top.pack(fill="x", padx=16, pady=12)
        brand = tk.Frame(top, bg=COLORS["shell"])
        brand.pack(side="left", padx=(0, 28))
        tk.Label(brand, text="AETHERION", bg=COLORS["shell"], fg=COLORS["text"],
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(brand, text="S T U D I O   /   0 3", bg=COLORS["shell"],
                 fg=COLORS["accent"], font=("Consolas", 8)).pack(anchor="w")
        self.nav_buttons = {}
        self.nav_indicators = {}
        self.active_view = "dashboard"
        for name, view in (("Workspace", "dashboard"), ("Models", "models"),
                           ("Benchmark", "benchmarks"), ("Results", "results")):
            cell = tk.Frame(top, bg=COLORS["shell"])
            cell.pack(side="left", padx=4)
            button = self._button(cell, name, lambda key=view: self.focus_section(key))
            button.pack(fill="x")
            marker = tk.Frame(cell, height=2, bg=COLORS["shell"])
            marker.pack(fill="x", pady=(6, 0))
            self.nav_buttons[view] = button
            self.nav_indicators[view] = marker
        utility = tk.Frame(bar, bg=COLORS["shell"])
        utility.pack(fill="x", padx=16, pady=(0, 10))
        tk.Label(utility, text="LOCAL FIRST   /   YOUR DATA, YOUR DEVICE", bg=COLORS["shell"],
                 fg=COLORS["muted"], font=FONTS["small"]).pack(side="left")
        for name, view in (("Hardware", "hardware"), ("History", "history"), ("Settings", "settings")):
            cell = tk.Frame(utility, bg=COLORS["shell"])
            cell.pack(side="right", padx=4)
            button = self._button(cell, name, lambda key=view: self.focus_section(key))
            button.configure(pady=5)
            button.pack()
            marker = tk.Frame(cell, height=2, bg=COLORS["shell"])
            marker.pack(fill="x")
            self.nav_buttons[view] = button
            self.nav_indicators[view] = marker
        if self.auth_session is not None:
            self._button(top, "Sign out", self.sign_out).pack(side="right")

    def build_studio_home(self) -> None:
        self.lab_view = self.dashboard_view
        self.lab_view.pack_forget()
        self.views["benchmarks"] = self.lab_view
        home = tk.Frame(self.view_stack, bg=COLORS["canvas"])
        self.dashboard_view = home
        self.views["dashboard"] = home
        scroll = ttk.Scrollbar(home, orient="vertical", style="Aetherion.Vertical.TScrollbar")
        scroll.pack(side="right", fill="y")
        self.home_canvas = tk.Canvas(home, bg=COLORS["canvas"], bd=0, highlightthickness=0)
        self.home_canvas.pack(fill="both", expand=True)
        self.home_canvas.configure(yscrollcommand=scroll.set)
        scroll.configure(command=self.home_canvas.yview)
        home = tk.Frame(self.home_canvas, bg=COLORS["canvas"])
        home_window = self.home_canvas.create_window((0, 0), window=home, anchor="nw")
        home.bind("<Configure>", lambda _event: self.home_canvas.configure(scrollregion=self.home_canvas.bbox("all")))
        self.home_canvas.bind("<Configure>", lambda event: self.home_canvas.itemconfigure(home_window, width=event.width))
        self.root.bind_all("<MouseWheel>", self._scroll_home, add="+")
        self.root.bind_all("<FocusIn>", self._reveal_home_focus, add="+")
        home.grid_columnconfigure(0, weight=1)
        home.grid_rowconfigure(2, weight=1)

        # The first screen is a launchpad. Configuration and trace live in the lab.
        hero = tk.Frame(home, bg=COLORS["canvas"])
        hero.grid(row=0, column=0, sticky="ew", pady=(0, 24))
        hero.grid_columnconfigure(0, weight=3)
        hero.grid_columnconfigure(1, weight=2)
        introduction = tk.Frame(hero, bg=COLORS["canvas"])
        introduction.grid(row=0, column=0, sticky="nsew", padx=(0, 24))
        tk.Label(introduction, text="BUILT AROUND YOUR MACHINE", bg=COLORS["canvas"],
                 fg=COLORS["accent"], font=FONTS["section"]).pack(anchor="w")
        tk.Label(introduction, text="Make your next\nmodel a better fit.", bg=COLORS["canvas"],
                 fg=COLORS["text"], font=("Segoe UI", 34, "bold"), justify="left").pack(anchor="w", pady=(8, 12))
        copy = tk.Label(introduction, text="Explore your models. Test their strengths.\nChoose with evidence from your own hardware.",
                        bg=COLORS["canvas"], fg=COLORS["muted"], font=("Segoe UI", 11), justify="left")
        copy.pack(anchor="w", fill="x")
        introduction.bind("<Configure>", lambda event: copy.configure(wraplength=max(160, event.width)))

        featured = self._card(hero, accent=True)
        featured.grid(row=0, column=1, sticky="nsew")
        body = tk.Frame(featured, bg=COLORS["surface"])
        body.pack(fill="both", expand=True, padx=24, pady=20)
        tk.Label(body, text="YOUR STARTING POINT", bg=COLORS["surface"], fg=COLORS["accent"], font=FONTS["section"]).pack(anchor="w")
        self.featured_name = tk.Label(body, text="Discover your models", bg=COLORS["surface"], fg=COLORS["text"],
                                      font=("Segoe UI", 21, "bold"), justify="left", anchor="w")
        self.featured_name.pack(fill="x", pady=(12, 8))
        self.featured_fit = tk.Label(body, text="Your local collection will appear here.", bg=COLORS["surface"],
                                     fg=COLORS["muted"], font=FONTS["body"], justify="left", anchor="w")
        self.featured_fit.pack(fill="x", pady=(0, 16))
        self.featured_action = self._button(body, "Explore models", lambda: self.focus_section("models"), primary=True)
        self.featured_action.pack(fill="x", side="bottom")
        body.bind("<Configure>", lambda event: [label.configure(wraplength=max(160, event.width))
                                                for label in (self.featured_name, self.featured_fit)])

        machine = self._card(home)
        machine.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        machine_body = tk.Frame(machine, bg=COLORS["surface"])
        machine_body.pack(fill="x", padx=20, pady=14)
        hardware = self.session.hardware
        gpu = next((g for g in hardware.get("gpu", []) if g.get("name") != "UNKNOWN"), {})
        ram = hardware.get("memory", {}).get("total_gb")
        cpu = hardware.get("cpu", {}).get("model", "CPU telemetry unavailable")
        tk.Label(machine_body, text="THIS MACHINE", bg=COLORS["surface"], fg=COLORS["accent"],
                 font=FONTS["section"]).pack(side="left", padx=(0, 20))
        details = tk.Label(machine_body, text=f"{gpu.get('name', 'No GPU detected')}   /   {f'{ram} GB RAM' if ram is not None else 'RAM unavailable'}\n{cpu}",
                           bg=COLORS["surface"], fg=COLORS["text_soft"], font=FONTS["small"], justify="left", anchor="w")
        self._button(machine_body, "View hardware", lambda: self.focus_section("hardware")).pack(side="right", padx=(12, 0))
        details.pack(side="left", fill="x", expand=True)
        details.bind("<Configure>", lambda event: details.configure(wraplength=max(120, event.width)))

        bottom = tk.Frame(home, bg=COLORS["canvas"])
        bottom.grid(row=2, column=0, sticky="nsew")
        bottom.grid_columnconfigure(0, weight=3)
        bottom.grid_columnconfigure(1, weight=2)
        bottom.grid_rowconfigure(0, weight=1)
        activity = self._card(bottom)
        activity.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        activity_body = tk.Frame(activity, bg=COLORS["surface"])
        activity_body.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(activity_body, text="Recent experiments", bg=COLORS["surface"], fg=COLORS["text"],
                 font=("Segoe UI", 16, "bold")).pack(anchor="w")
        tk.Label(activity_body, text="A record of what your machine can do.", bg=COLORS["surface"],
                 fg=COLORS["muted"], font=FONTS["small"]).pack(anchor="w", pady=(4, 12))
        self.home_activity = tk.Frame(activity_body, bg=COLORS["surface"])
        self.home_activity.pack(fill="both", expand=True)
        readiness = self._card(bottom)
        readiness.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ready_body = tk.Frame(readiness, bg=COLORS["surface"])
        ready_body.pack(fill="both", expand=True, padx=20, pady=18)
        tk.Label(ready_body, text="A clear path to your first run", bg=COLORS["surface"], fg=COLORS["text"],
                 font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 12))
        self.readiness_labels = []
        for number, title in (("01", "Find a local model"), ("02", "Choose what to test"), ("03", "Measure and compare")):
            row = tk.Frame(ready_body, bg=COLORS["surface"])
            row.pack(fill="x", pady=7)
            tk.Label(row, text=number, fg=COLORS["accent"], bg=COLORS["surface"], font=("Consolas", 13, "bold")).pack(side="left", padx=(0, 12))
            label = tk.Label(row, text=title, fg=COLORS["text_soft"], bg=COLORS["surface"], font=FONTS["body"], anchor="w")
            label.pack(side="left", fill="x", expand=True)
            self.readiness_labels.append(label)
        self._button(ready_body, "Open benchmark lab", lambda: self.focus_section("benchmarks")).pack(side="bottom", fill="x", pady=(12, 0))
        self.refresh_studio_home()
        self.focus_section("dashboard")

    def prepare_model(self, name: str) -> None:
        if self.busy:
            return
        if name in self.models:
            self.model_var.set(name)
            self.update_model_details()
            self.focus_section("benchmarks")

    def sync_studio_actions(self) -> None:
        state = "disabled" if self.busy else "normal"
        for name in ("featured_action", "catalog_refresh_button"):
            widget = getattr(self, name, None)
            if widget is not None:
                widget.configure(state=state)
        for widget in getattr(self, "catalog_use_buttons", []):
            if widget.winfo_exists():
                widget.configure(state=state)

    def _scroll_home(self, event: tk.Event) -> None:
        canvas = self.home_canvas
        if canvas.winfo_ismapped() and canvas.winfo_rootx() <= event.x_root <= canvas.winfo_rootx() + canvas.winfo_width() and canvas.winfo_rooty() <= event.y_root <= canvas.winfo_rooty() + canvas.winfo_height():
            canvas.yview_scroll(int(-event.delta / 120), "units")

    def _reveal_home_focus(self, event: tk.Event) -> None:
        widget = event.widget
        if not self.home_canvas.winfo_ismapped() or not str(widget).startswith(str(self.home_canvas) + "."):
            return
        top = widget.winfo_rooty() - self.home_canvas.winfo_rooty()
        bottom = top + widget.winfo_height()
        viewport = self.home_canvas.winfo_height()
        bounds = self.home_canvas.bbox("all")
        if bounds and bounds[3] > 0 and (top < 0 or bottom > viewport):
            current = self.home_canvas.canvasy(0)
            offset = top - 8 if top < 0 else bottom - viewport + 8
            self.home_canvas.yview_moveto(max(0, current + offset) / bounds[3])

    def refresh_studio_home(self) -> None:
        if not hasattr(self, "featured_name"):
            return
        model = self.models.get(self.recommended_model_name)
        if model is not None:
            self.featured_name.configure(text=model.name)
            self.featured_fit.configure(text=f"{model.provider.upper()}  /  {self.model_fit_summary(self.assess_model(model))}\nHardware fit is an estimate; benchmark to verify.")
            self.featured_action.configure(text="Configure this benchmark", command=lambda name=model.name: self.prepare_model(name))
        else:
            self.featured_name.configure(text="Your collection starts here.")
            self.featured_fit.configure(text="Download a GGUF model or refresh your installed Ollama models.")
            self.featured_action.configure(text="Find your first model", command=self.open_model_downloader)
        self.featured_action.configure(state="disabled" if self.busy else "normal")
        self.readiness_labels[0].configure(text=f"{len(self.models)} local models found" if self.models else "Find a local model")
        for child in self.home_activity.winfo_children():
            child.destroy()
        rows = sorted(self.session.store.list(), key=lambda row: row.get("created_at", ""), reverse=True)[:3]
        if not rows:
            tk.Label(self.home_activity, text="No experiments yet.", bg=COLORS["surface"], fg=COLORS["text"],
                     font=("Segoe UI", 18, "bold"), anchor="w").pack(fill="x", pady=(18, 8))
            tk.Label(self.home_activity, text="Your first benchmark will turn this space\ninto a useful performance history.",
                     bg=COLORS["surface"], fg=COLORS["muted"], font=FONTS["body"], justify="left", anchor="w").pack(fill="x")
        for record in rows:
            row = tk.Frame(self.home_activity, bg=COLORS["surface"])
            row.pack(fill="x", pady=6)
            tk.Label(row, text=str(record.get("status", "unknown")).upper(), bg=COLORS["surface_interactive"],
                     fg=COLORS["text_soft"], font=FONTS["small"], padx=8, pady=6).pack(side="right")
            title = tk.Label(row, text=str(record.get("benchmark", "Unknown model")), bg=COLORS["surface"],
                             fg=COLORS["text"], font=FONTS["body"], anchor="w", justify="left")
            title.pack(fill="x")
            title.bind("<Configure>", lambda event, label=title: label.configure(wraplength=max(100, event.width)))
            result = record.get("result", {})
            rate = result.get("average_tokens_per_second")
            speed = f"{rate:.2f} tokens/s" if isinstance(rate, (float, int)) else "Speed unavailable"
            tk.Label(row, text=f"{result.get('passed_checks', 0)}/{result.get('task_count', 0)} checks passed  /  {speed}",
                     bg=COLORS["surface"], fg=COLORS["muted"], font=FONTS["small"], anchor="w").pack(fill="x", pady=(4, 0))

    def create_model_catalog(self, parent: tk.Widget) -> None:
        tools = tk.Frame(parent, bg=COLORS["surface"])
        tools.pack(fill="x", padx=20, pady=16)
        self._field_label(tools, "Search your collection").pack(anchor="w", pady=(0, 6))
        self.model_search = tk.StringVar()
        search = tk.Entry(tools, textvariable=self.model_search, bg=COLORS["surface_elevated"], fg=COLORS["text"],
                          insertbackground=COLORS["accent"], font=FONTS["body"], relief="flat",
                          highlightthickness=1, highlightbackground=COLORS["line_strong"], highlightcolor=COLORS["accent"])
        search.pack(side="left", fill="x", expand=True, ipady=10, padx=(0, 12))
        self.catalog_refresh_button = self._button(tools, "Refresh", self.refresh_models)
        self.catalog_refresh_button.pack(side="left", padx=(0, 8))
        self._button(tools, "Add a model", self.open_model_downloader, primary=True).pack(side="left")
        self.model_search.trace_add("write", lambda *_args: self.refresh_model_cards())
        viewport = tk.Frame(parent, bg=COLORS["surface"])
        viewport.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.catalog_canvas = tk.Canvas(viewport, bg=COLORS["surface"], bd=0, highlightthickness=0)
        scroll = ttk.Scrollbar(viewport, orient="vertical", command=self.catalog_canvas.yview, style="Aetherion.Vertical.TScrollbar")
        scroll.pack(side="right", fill="y")
        self.catalog_canvas.pack(fill="both", expand=True)
        self.catalog_canvas.configure(yscrollcommand=scroll.set)
        self.model_cards = tk.Frame(self.catalog_canvas, bg=COLORS["surface"])
        window = self.catalog_canvas.create_window((0, 0), window=self.model_cards, anchor="nw")
        self.model_cards.bind("<Configure>", lambda _event: self.catalog_canvas.configure(scrollregion=self.catalog_canvas.bbox("all")))
        self.catalog_canvas.bind("<Configure>", lambda event: self.catalog_canvas.itemconfigure(window, width=event.width))
        self.root.bind_all("<MouseWheel>", self._scroll_catalog, add="+")

    def _scroll_catalog(self, event: tk.Event) -> None:
        canvas = self.catalog_canvas
        if canvas.winfo_ismapped() and canvas.winfo_rootx() <= event.x_root <= canvas.winfo_rootx() + canvas.winfo_width() and canvas.winfo_rooty() <= event.y_root <= canvas.winfo_rooty() + canvas.winfo_height():
            canvas.yview_scroll(int(-event.delta / 120), "units")

    def refresh_model_cards(self) -> None:
        if not hasattr(self, "model_cards"):
            return
        for child in self.model_cards.winfo_children():
            child.destroy()
        self.catalog_use_buttons = []
        for col in range(2):
            self.model_cards.grid_columnconfigure(col, weight=1, uniform="model-cards")
        query = self.model_search.get().strip().casefold()
        matches = [model for model in self.models.values() if query in model.name.casefold() or query in model.provider.casefold()]
        if not matches:
            message = "No models match this search." if self.models else "Your library is empty. Add a model to get started."
            tk.Label(self.model_cards, text=message, bg=COLORS["surface"], fg=COLORS["muted"],
                     font=("Segoe UI", 16), padx=20, pady=32).grid(row=0, column=0, columnspan=2)
        for index, model in enumerate(matches):
            card = self._card(self.model_cards)
            card.grid(row=index//2, column=index%2, sticky="nsew", padx=6, pady=6)
            body = tk.Frame(card, bg=COLORS["surface"])
            body.pack(fill="both", expand=True, padx=20, pady=20)
            tk.Label(body, text=f"{model.provider.upper()}  /  {model.details.get('quantization_level') or 'LOCAL MODEL'}",
                     bg=COLORS["surface"], fg=COLORS["accent"], font=FONTS["section"]).pack(anchor="w")
            name = tk.Label(body, text=model.name, bg=COLORS["surface"], fg=COLORS["text"], font=("Segoe UI", 19, "bold"), anchor="w", justify="left")
            name.pack(fill="x", pady=(10, 12))
            size = f"{model.size_bytes / 1024**3:.2f} GB" if model.size_bytes else "Size unavailable"
            fit = tk.Label(body, text=f"{size}\n{self.model_fit_summary(self.assess_model(model))}", bg=COLORS["surface"], fg=COLORS["muted"],
                           font=FONTS["body"], anchor="w", justify="left")
            fit.pack(fill="x", pady=(0, 16))
            body.bind("<Configure>", lambda event, labels=(name, fit): [label.configure(wraplength=max(120, event.width)) for label in labels])
            button = self._button(body, "Use in benchmark", lambda name=model.name: self.prepare_model(name))
            self.catalog_use_buttons.append(button)
            button.pack(fill="x", side="bottom")
            button.configure(state="disabled" if self.busy else "normal")

    def create_results_board(self, parent: tk.Widget) -> None:
        self._button(parent, "Open selected record", self.open_selected_result).pack(side="bottom", anchor="e", padx=20, pady=(0, 16))
        self.results_chart = tk.Canvas(parent, height=210, bg=COLORS["surface"], bd=0, highlightthickness=0)
        self.results_chart.pack(fill="x", padx=20, pady=(20, 12))
        self.results_chart.bind("<Configure>", lambda _event: self.paint_results_chart())
        sorting = tk.Frame(parent, bg=COLORS["surface"])
        sorting.pack(fill="x", padx=20, pady=(0, 12))
        self._field_label(sorting, "Order records").pack(side="left", padx=(0, 12))
        self.result_order = tk.StringVar(value="Newest first")
        order = ttk.Combobox(sorting, textvariable=self.result_order, state="readonly", style="Aetherion.TCombobox",
                             values=("Newest first", "Fastest first", "Most checks passed", "Model A–Z"))
        order.pack(side="left")
        order.bind("<<ComboboxSelected>>", lambda _event: self.sort_result_records())
        viewport = tk.Frame(parent, bg=COLORS["surface"])
        viewport.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.results_table = ttk.Treeview(viewport, columns=("model", "state", "checks", "speed"), show="headings", style="Studio.Treeview")
        for key, title, width in (("model", "MODEL", 300), ("state", "STATUS", 100), ("checks", "CHECKS PASSED", 140), ("speed", "TOKENS / SECOND", 160)):
            self.results_table.heading(key, text=title)
            self.results_table.column(key, width=width, minwidth=80, stretch=True)
        # Table uses native keyboard navigation; double-click opens its saved record.
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=self.results_table.yview, style="Aetherion.Vertical.TScrollbar")
        scrollbar.pack(side="right", fill="y")
        self.results_table.configure(yscrollcommand=scrollbar.set)
        self.results_table.pack(fill="both", expand=True)
        self.results_table.bind("<Double-1>", lambda _event: self.open_selected_result())
        self.results_table.bind("<Return>", lambda _event: self.open_selected_result())

    def refresh_results_board(self) -> None:
        if not hasattr(self, "results_table"):
            return
        rows = sorted(self.session.store.list(), key=lambda row: row.get("created_at", ""), reverse=True)
        self.result_rows = {str(i): row for i, row in enumerate(rows)}
        self.results_table.delete(*self.results_table.get_children())
        for key, row in self.result_rows.items():
            result = row.get("result", {})
            rate = result.get("average_tokens_per_second")
            self.results_table.insert("", "end", iid=key, values=(row.get("benchmark", "Unknown"), row.get("status", "Unknown"),
                f"{result.get('passed_checks', 0)} / {result.get('task_count', 0)}", f"{rate:.2f}" if isinstance(rate, (int, float)) else "Unavailable"))
        self.sort_result_records()
        self.paint_results_chart()
        self.refresh_studio_home()

    def sort_result_records(self) -> None:
        mode = self.result_order.get()
        def sort_key(item):
            row = item[1]
            result = row.get("result", {})
            if mode == "Model A–Z":
                return str(row.get("benchmark", "")).casefold()
            if mode == "Fastest first":
                speed = result.get("average_tokens_per_second")
                return speed if isinstance(speed, (int, float)) else -1
            if mode == "Most checks passed":
                return result.get("passed_checks", 0)
            return row.get("created_at", "")
        ordered = sorted(getattr(self, "result_rows", {}).items(), key=sort_key, reverse=mode != "Model A–Z")
        for index, (key, _row) in enumerate(ordered):
            self.results_table.move(key, "", index)

    def open_selected_result(self) -> None:
        import webbrowser
        selection = self.results_table.selection()
        if not selection:
            return
        record = self.result_rows.get(selection[0], {})
        path = next(self.session.store.base_dir.glob(f"**/{record.get('run_id', '')}.json"), None)
        if path:
            webbrowser.open(path.resolve().as_uri())

    def paint_results_chart(self) -> None:
        canvas = self.results_chart
        canvas.delete("all")
        width = max(400, canvas.winfo_width())
        canvas.create_text(0, 8, text="Measured generation speed", fill=COLORS["text"], font=("Segoe UI", 16, "bold"), anchor="nw")
        canvas.create_text(0, 38, text="Latest measured run per model / tokens per second / suites may differ", fill=COLORS["muted"], font=FONTS["small"], anchor="nw")
        measured = {}
        for row in getattr(self, "result_rows", {}).values():
            rate = row.get("result", {}).get("average_tokens_per_second")
            if isinstance(rate, (int, float)) and rate >= 0:
                measured.setdefault(row.get("benchmark", "Unknown"), rate)
        ranked = sorted(measured.items(), key=lambda item: item[1], reverse=True)[:4]
        if not ranked:
            canvas.create_text(0, 95, text="No measured speeds yet.", fill=COLORS["text_soft"], font=("Segoe UI", 20, "bold"), anchor="nw")
            canvas.create_text(0, 135, text="Run a benchmark to build your performance comparison.", fill=COLORS["muted"], font=FONTS["body"], anchor="nw")
            return
        highest = max(1, ranked[0][1])
        for i, (name, speed) in enumerate(ranked):
            y = 77 + i * 32
            chart_name = name if len(name) <= 27 else name[:24] + "…"
            canvas.create_text(0, y, text=chart_name, fill=COLORS["text_soft"], font=FONTS["small"], anchor="w")
            length = (width - 300) * speed / highest
            canvas.create_rectangle(210, y-7, width-80, y+7, fill=COLORS["surface_elevated"], outline="")
            canvas.create_rectangle(210, y-7, 210+length, y+7, fill=COLORS["accent"], outline="")
            canvas.create_text(width-8, y, text=f"{speed:.2f}", fill=COLORS["text"], font=FONTS["mono"], anchor="e")
