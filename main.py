import customtkinter as ctk
from tkinter import ttk
import api

class SimpleAlchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SimpleAlch - OSRS High Alchemy Tool")
        self.geometry("1350x780")          # More compact
        self.minsize(1250, 700)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.settings = {
            "nature_price": "",
            "fire_method": "staff",
            "fire_price": "",
            "price_type": "average",
        }

        self.mapping_data = {}
        self.latest_data = {}
        self.all_items = []
        self.current_page = 1
        self.items_per_page = 100

        self._create_top_bar()
        self._create_pagination_controls()
        self._create_main_area()
        self._create_status_bar()

        self.after(500, self.load_initial_data)

    def _create_top_bar(self):
        self.top_bar = ctk.CTkFrame(self, height=45, corner_radius=0)
        self.top_bar.pack(fill="x")

        title_label = ctk.CTkLabel(self.top_bar, text="SimpleAlch", 
                                   font=ctk.CTkFont(size=18, weight="bold"))
        title_label.pack(side="left", padx=15)

        self.refresh_btn = ctk.CTkButton(self.top_bar, text="Refresh Prices", width=110,
                                         command=self.refresh_prices)
        self.refresh_btn.pack(side="right", padx=8, pady=6)

        self.config_btn = ctk.CTkButton(self.top_bar, text="⚙ Configuration", width=130,
                                        command=self.open_configuration)
        self.config_btn.pack(side="right", padx=8, pady=6)

    def _create_pagination_controls(self):
        self.pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.pagination_frame.pack(fill="x", padx=12, pady=(3, 0))

        ctk.CTkLabel(self.pagination_frame, text="Show:").pack(side="left", padx=(0, 4))
        self.items_per_page_var = ctk.StringVar(value="100")
        items_menu = ctk.CTkOptionMenu(
            self.pagination_frame, values=["50", "100", "150"],
            variable=self.items_per_page_var, width=65,
            command=self.change_items_per_page
        )
        items_menu.pack(side="left", padx=(0, 15))

        self.prev_btn = ctk.CTkButton(self.pagination_frame, text="<", width=35,
                                      command=self.prev_page)
        self.prev_btn.pack(side="left", padx=3)

        self.page_entry = ctk.CTkEntry(self.pagination_frame, width=45, justify="center")
        self.page_entry.pack(side="left", padx=4)
        self.page_entry.bind("<Return>", self.jump_to_page)

        self.page_label = ctk.CTkLabel(self.pagination_frame, text="/ 1", width=35)
        self.page_label.pack(side="left", padx=2)

        self.next_btn = ctk.CTkButton(self.pagination_frame, text=">", width=35,
                                      command=self.next_page)
        self.next_btn.pack(side="left", padx=3)

        self.total_label = ctk.CTkLabel(self.pagination_frame, text="Total items: 0")
        self.total_label.pack(side="left", padx=15)

    def _create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=6)
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        columns = ("members", "name", "high_alch", "ge_price", "profit", "total_profit", "total_investment", "buy_limit")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=24)

        self.tree.heading("members", text="M")
        self.tree.heading("name", text="Item")
        self.tree.heading("high_alch", text="High Alch")
        self.tree.heading("ge_price", text="GE Price")
        self.tree.heading("profit", text="Profit/Cast")
        self.tree.heading("total_profit", text="Total Profit")
        self.tree.heading("total_investment", text="Total Investment")
        self.tree.heading("buy_limit", text="Buy Limit")

        self.tree.column("members", width=45, anchor="center", stretch=False)
        self.tree.column("name", width=220)
        self.tree.column("high_alch", width=75, anchor="center")
        self.tree.column("ge_price", width=75, anchor="center")
        self.tree.column("profit", width=80, anchor="center")
        self.tree.column("total_profit", width=95, anchor="center")
        self.tree.column("total_investment", width=105, anchor="center")
        self.tree.column("buy_limit", width=65, anchor="center", stretch=False)

        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.sort_by_column(c))

        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

    def _create_status_bar(self):
        self.status_bar = ctk.CTkLabel(self, text="Loading...", anchor="w", font=ctk.CTkFont(size=11))
        self.status_bar.pack(fill="x", padx=12, pady=(0, 6))

    # ==================== PAGINATION ====================
    def change_items_per_page(self, value):
        self.items_per_page = int(value)
        self.current_page = 1
        self.populate_table()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.populate_table()

    def next_page(self):
        total_pages = self.get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self.populate_table()

    def jump_to_page(self, event=None):
        try:
            page = int(self.page_entry.get())
            total_pages = self.get_total_pages()
            if 1 <= page <= total_pages:
                self.current_page = page
                self.populate_table()
            else:
                self.page_entry.delete(0, "end")
                self.page_entry.insert(0, str(self.current_page))
        except ValueError:
            self.page_entry.delete(0, "end")
            self.page_entry.insert(0, str(self.current_page))

    def get_total_pages(self):
        if not self.all_items:
            return 1
        return max(1, (len(self.all_items) + self.items_per_page - 1) // self.items_per_page)

    def update_pagination_ui(self):
        total_pages = self.get_total_pages()
        self.page_label.configure(text=f"/ {total_pages}")
        self.page_entry.delete(0, "end")
        self.page_entry.insert(0, str(self.current_page))
        self.total_label.configure(text=f"Total items: {len(self.all_items)}")

        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages else "disabled")

    # ==================== DATA HANDLING ====================
    def load_initial_data(self):
        self.status_bar.configure(text="Loading data from API (with cache)...")
        self.mapping_data = api.fetch_mapping() or {}
        self.latest_data = api.fetch_latest() or {}

        if self.mapping_data and self.latest_data:
            filtered_items = []
            for item_id, item in self.mapping_data.items():
                if str(item_id) in self.latest_data:
                    price = api.get_item_price(self.latest_data, item_id)
                    buy_limit = item.get("limit", 0) or 0
                    high_alch = item.get("highalch", 0)

                    if price and price > 0 and buy_limit > 0 and high_alch > 0:
                        filtered_items.append((item_id, item))

            self.all_items = sorted(filtered_items, key=lambda x: x[1].get("name", "").lower())
            self.status_bar.configure(text=f"Loaded {len(self.all_items)} tradeable items")
            self.current_page = 1
            self.populate_table()
        else:
            self.status_bar.configure(text="Failed to load data from API")

    def refresh_prices(self):
        self.status_bar.configure(text="Refreshing prices...")
        self.latest_data = api.fetch_latest() or {}
        self.populate_table()
        self.status_bar.configure(text="Prices refreshed")

    def populate_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.all_items:
            return

        nature_cost = int(self.settings["nature_price"]) if self.settings["nature_price"].isdigit() else 0
        fire_cost = int(self.settings["fire_price"]) if self.settings["fire_price"].isdigit() else 0
        rune_cost = nature_cost + fire_cost if self.settings["fire_method"] == "pay" else nature_cost
        price_type = self.settings["price_type"]

        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_items = self.all_items[start:end]

        for item_id, item in page_items:
            name = item.get("name", "Unknown")
            high_alch = item.get("highalch", 0)
            buy_limit = item.get("limit", 0) or 0
            is_members = item.get("members", False)

            ge_price = api.get_item_price(self.latest_data, item_id, price_type) or 0
            profit = high_alch - ge_price - rune_cost
            total_profit = profit * buy_limit if buy_limit else 0
            total_investment = ge_price * buy_limit if buy_limit else 0

            members_display = "★" if is_members else ""

            self.tree.insert("", "end", values=(
                members_display, name, high_alch, ge_price, profit, total_profit, total_investment, buy_limit
            ))

        self.update_pagination_ui()

    def sort_by_column(self, col):
        reverse = not getattr(self, f"_sort_reverse_{col}", False)
        setattr(self, f"_sort_reverse_{col}", reverse)

        def get_sort_value(item_tuple):
            item_id, data = item_tuple
            if col == "name":
                return data.get("name", "").lower()
            elif col == "members":
                return data.get("members", False)
            elif col == "high_alch":
                return data.get("highalch", 0)
            elif col == "buy_limit":
                return data.get("limit", 0) or 0
            else:
                price_type = self.settings["price_type"]
                ge_price = api.get_item_price(self.latest_data, item_id, price_type) or 0
                nature_cost = int(self.settings["nature_price"]) if self.settings["nature_price"].isdigit() else 0
                fire_cost = int(self.settings["fire_price"]) if self.settings["fire_price"].isdigit() else 0
                rune_cost = nature_cost + fire_cost if self.settings["fire_method"] == "pay" else nature_cost

                profit = data.get("highalch", 0) - ge_price - rune_cost
                buy_limit = data.get("limit", 0) or 0

                if col == "ge_price":
                    return ge_price
                elif col == "profit":
                    return profit
                elif col == "total_profit":
                    return profit * buy_limit
                elif col == "total_investment":
                    return ge_price * buy_limit
                return 0

        self.all_items.sort(key=get_sort_value, reverse=reverse)
        self.current_page = 1
        self.populate_table()

    # ==================== CONFIGURATION ====================
    def open_configuration(self):
        self.config_window = ctk.CTkToplevel(self)
        self.config_window.title("Configuration")
        self.config_window.geometry("560x520")     # More compact
        self.config_window.resizable(False, False)
        self.config_window.transient(self)
        self.config_window.grab_set()

        price_type = self.settings.get("price_type", "average")
        nature_api_price = api.get_item_price(self.latest_data, 561, price_type) or 0
        fire_api_price = api.get_item_price(self.latest_data, 554, price_type) or 0

        ctk.CTkLabel(self.config_window, text="Configuration", 
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self.price_label = ctk.CTkLabel(
            self.config_window,
            text=f"Current API Prices ({price_type.capitalize()}):   Nature: {nature_api_price} gp   |   Fire: {fire_api_price} gp",
            font=ctk.CTkFont(size=11),
            text_color="#AAAAAA"
        )
        self.price_label.pack(pady=(0, 10))

        # Nature Rune
        ctk.CTkLabel(self.config_window, text="Nature Rune Price (gp)").pack(anchor="w", padx=25)
        nature_frame = ctk.CTkFrame(self.config_window, fg_color="transparent")
        nature_frame.pack(fill="x", padx=25, pady=3)
        self.nature_entry = ctk.CTkEntry(nature_frame)
        self.nature_entry.pack(side="left", fill="x", expand=True)
        self.nature_entry.insert(0, self.settings.get("nature_price", ""))
        ctk.CTkLabel(nature_frame, text="(Leave empty = API)", text_color="gray").pack(side="left", padx=6)

        save_nature_btn = ctk.CTkButton(nature_frame, text="Save", width=55,
                                        command=self.save_nature_price)
        save_nature_btn.pack(side="left", padx=6)

        # Fire Rune Method
        ctk.CTkLabel(self.config_window, text="Fire Rune Method").pack(anchor="w", padx=25, pady=(8, 0))
        self.fire_method_var = ctk.StringVar(value=self.settings.get("fire_method", "staff"))
        ctk.CTkRadioButton(self.config_window, text="Use Fire Staff / Tome of Fire (Free)", 
                           variable=self.fire_method_var, value="staff",
                           command=self.update_settings_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="Pay for Fire Runes", 
                           variable=self.fire_method_var, value="pay",
                           command=self.update_settings_live).pack(anchor="w", padx=25)

        # Fire Rune Price
        ctk.CTkLabel(self.config_window, text="Fire Rune Price (if paying)").pack(anchor="w", padx=25, pady=(8, 0))
        fire_frame = ctk.CTkFrame(self.config_window, fg_color="transparent")
        fire_frame.pack(fill="x", padx=25, pady=3)
        self.fire_entry = ctk.CTkEntry(fire_frame)
        self.fire_entry.pack(side="left", fill="x", expand=True)
        self.fire_entry.insert(0, self.settings.get("fire_price", ""))
        ctk.CTkLabel(fire_frame, text="(Leave empty = API)", text_color="gray").pack(side="left", padx=6)

        save_fire_btn = ctk.CTkButton(fire_frame, text="Save", width=55,
                                      command=self.save_fire_price)
        save_fire_btn.pack(side="left", padx=6)

        # GE Price Type
        ctk.CTkLabel(self.config_window, text="GE Price Type").pack(anchor="w", padx=25, pady=(8, 0))
        self.price_type_var = ctk.StringVar(value=self.settings.get("price_type", "average"))
        ctk.CTkRadioButton(self.config_window, text="Low Price", variable=self.price_type_var, value="low",
                           command=self.update_price_type_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="High Price", variable=self.price_type_var, value="high",
                           command=self.update_price_type_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="Average (Recommended)", variable=self.price_type_var, value="average",
                           command=self.update_price_type_live).pack(anchor="w", padx=25)

    # ==================== LIVE UPDATE METHODS ====================
    def update_settings_live(self):
        self.settings["fire_method"] = self.fire_method_var.get()
        self.populate_table()

    def update_price_type_live(self):
        self.settings["price_type"] = self.price_type_var.get()
        self.populate_table()
        price_type = self.settings["price_type"]
        nature_api_price = api.get_item_price(self.latest_data, 561, price_type) or 0
        fire_api_price = api.get_item_price(self.latest_data, 554, price_type) or 0
        self.price_label.configure(
            text=f"Current API Prices ({price_type.capitalize()}):   Nature: {nature_api_price} gp   |   Fire: {fire_api_price} gp"
        )

    def save_nature_price(self):
        self.settings["nature_price"] = self.nature_entry.get().strip()
        self.populate_table()

    def save_fire_price(self):
        self.settings["fire_price"] = self.fire_entry.get().strip()
        self.populate_table()


if __name__ == "__main__":
    app = SimpleAlchApp()
    app.mainloop()