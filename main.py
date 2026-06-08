# Load the external tools and libraries the program needs to run
import customtkinter as ctk
from tkinter import ttk, Menu
import api
import json
import os
import tkinter as tk
import datetime

# Set the config/cache file
CONFIG_FILE = "config.json"

# Creates the main window using CustomTkinter
class SimpleAlchApp(ctk.CTk):
    # This code runs automatically when the app starts
    def __init__(self):
        super().__init__()
        # Sets the window title, size, and minimum size
        self.title("SimpleAlch - OSRS High Alchemy Tool")
        self.geometry("1125x800")
        self.minsize(1125, 300)
        # Applies the dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        # Stores all user preferences
        self.settings = {
            "nature_price": "",
            "fire_method": "staff",
            "fire_price": "",
            "price_type": "average",
            "volume_type": "both",           # NEW
        }
        # Initializes empty variables for data
        self.mapping_data = {}
        self.latest_data = {}
        self.volume_data = {}                # NEW
        self.all_items = []
        self.item_tags = {}
        self.show_favorites_only = False
        self.hide_members = False
        self.current_page = 1
        self.items_per_page = 100
        self.search_query = ""
        # Smart Fast Sync variables
        self.runelite_sync_var = ctk.BooleanVar(value=self.settings.get("runelite_sync_enabled", False))
        self.fast_sync_active = False
        self.fast_sync_attempts = 0
        self.max_fast_sync_attempts = 60
    
        self.load_config()
        # Builds the UI
        self._create_top_bar()
        self._create_search_and_pagination()
        self._create_main_area()
        self._create_status_bar()
        # Schedules initial data and background auto-refresh after startup
        self.after(500, self.load_initial_data)
        self.after(60000, self.background_auto_refresh)

        # RuneLite Sync initialization (limpio - una sola carga)
        self.runelite_sync_var = ctk.BooleanVar(value=self.settings.get("runelite_sync_enabled", False))

        if self.settings.get("runelite_sync_enabled", False) and self.settings.get("runelite_account"):
            # Solo cargamos los datos una vez al iniciar
            self.after(800, self.load_runelite_data)

    # Loads saved user settings and favorites from config.json when the app starts
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.settings = data.get("settings", self.settings)
                    self.item_tags = {int(k): v for k, v in data.get("item_tags", {}).items()}
            except Exception as e:
                print(f"Failed to load config: {e}")
    # Saves current settings and favorites (favorites + hidden items) into config.json
    def save_config(self):
        data = {
            "settings": self.settings,
            "item_tags": self.item_tags
        }
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    # Builds the top bar with title, Refresh button, Configuration button, Favorites Only checkbox, Hide Members checkbox, Clear Favorites, and Show Hidden buttons
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

        self.fav_only_var = ctk.BooleanVar(value=False)
        fav_check = ctk.CTkCheckBox(self.top_bar, text="Favorites Only", 
                                    variable=self.fav_only_var,
                                    command=self.toggle_favorites_filter)
        fav_check.pack(side="right", padx=12)

        hide_members_check = ctk.CTkCheckBox(self.top_bar, text="Hide Members", 
                                             command=self.toggle_hide_members)
        hide_members_check.pack(side="right", padx=8)

        clear_fav_btn = ctk.CTkButton(self.top_bar, text="Clear Favorites", width=110,
                                      command=self.clear_all_favorites)
        clear_fav_btn.pack(side="right", padx=8)

        show_hidden_btn = ctk.CTkButton(self.top_bar, text="Show Hidden", width=95,
                                        command=self.show_hidden_items)
        show_hidden_btn.pack(side="right", padx=8)
    # Creates the search bar, Clear button, items-per-page selector, and pagination controls (prev, page number, next, total items)
    def _create_search_and_pagination(self):
        self.search_pagination_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.search_pagination_frame.pack(fill="x", padx=12, pady=(3, 0))

        ctk.CTkLabel(self.search_pagination_frame, text="Search:").pack(side="left", padx=(0, 5))
        self.search_entry = ctk.CTkEntry(self.search_pagination_frame, width=250, placeholder_text="Search item name...")
        self.search_entry.pack(side="left", padx=(0, 8))
        self.search_entry.bind("<KeyRelease>", self.on_search)

        clear_btn = ctk.CTkButton(self.search_pagination_frame, text="Clear", width=55,
                                  command=self.clear_search)
        clear_btn.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(self.search_pagination_frame, text="Show:").pack(side="left", padx=(0, 4))
        self.items_per_page_var = ctk.StringVar(value="100")
        items_menu = ctk.CTkOptionMenu(
            self.search_pagination_frame, values=["50", "100", "150"],
            variable=self.items_per_page_var, width=65,
            command=self.change_items_per_page
        )
        items_menu.pack(side="left", padx=(0, 15))

        self.prev_btn = ctk.CTkButton(self.search_pagination_frame, text="<", width=35,
                                      command=self.prev_page)
        self.prev_btn.pack(side="left", padx=3)

        self.page_entry = ctk.CTkEntry(self.search_pagination_frame, width=45, justify="center")
        self.page_entry.pack(side="left", padx=4)
        self.page_entry.bind("<Return>", self.jump_to_page)

        self.page_label = ctk.CTkLabel(self.search_pagination_frame, text="/ 1", width=35)
        self.page_label.pack(side="left", padx=2)

        self.next_btn = ctk.CTkButton(self.search_pagination_frame, text=">", width=35,
                                      command=self.next_page)
        self.next_btn.pack(side="left", padx=3)

        self.total_label = ctk.CTkLabel(self.search_pagination_frame, text="Total items: 0")
        self.total_label.pack(side="left", padx=15)
    # Creates the main table (Treeview) with all columns including Daily Volume and sets up right-click menu
    def _create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=6)
        self.main_frame.pack(fill="both", expand=True, padx=12, pady=8)

        columns = ("favorite", "members", "name", "high_alch", "effective_price", "profit", 
                   "total_profit", "total_investment", "daily_volume", "bought_4h", "buy_limit")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=24)

        self.tree.heading("favorite", text="★")
        self.tree.heading("members", text="M")
        self.tree.heading("name", text="Item")
        self.tree.heading("high_alch", text="High Alch")
        self.tree.heading("effective_price", text="GE Price")
        self.tree.heading("profit", text="Profit/Cast")
        self.tree.heading("total_profit", text="Total Profit")
        self.tree.heading("total_investment", text="Total Investment")
        self.tree.heading("daily_volume", text="Daily Volume")
        self.tree.heading("bought_4h", text="Bought (4h)")
        self.tree.heading("buy_limit", text="Buy Limit")

        self.tree.column("favorite", width=35, anchor="center", stretch=False)
        self.tree.column("members", width=35, anchor="center", stretch=False)
        self.tree.column("name", width=220, stretch=False)
        self.tree.column("high_alch", width=110, anchor="center", stretch=False)
        self.tree.column("effective_price", width=110, anchor="center", stretch=False)
        self.tree.column("profit", width=110, anchor="center", stretch=False)
        self.tree.column("total_profit", width=110, anchor="center", stretch=False)
        self.tree.column("total_investment", width=110, anchor="center", stretch=False)
        self.tree.column("daily_volume", width=100, anchor="center", stretch=False)
        self.tree.column("bought_4h", width=80, anchor="center", stretch=False)
        self.tree.column("buy_limit", width=65, anchor="center", stretch=False)

        for col in columns:
            self.tree.heading(col, command=lambda c=col: self.sort_by_column(c))

        self.tree.bind("<Button-3>", self.show_context_menu)

        self.tree.pack(fill="both", expand=True, padx=8, pady=8)

        # Colores para la columna Bought (4h)
        self.tree.tag_configure("sold_out", background="#ff6b6b", foreground="white")
        self.tree.tag_configure("almost_full", background="#ffd93d")

    # Creates the bottom status bar that shows loading messages, sync status, etc
    def _create_status_bar(self):
        initial_text = "Loading... • Auto-refresh: Active"
        if self.settings.get("runelite_sync_enabled", False):
            account = self.settings.get("runelite_account", "")
            if account:
                initial_text += f"  •  RuneLite: {account}"

        self.status_bar = ctk.CTkLabel(self, text=initial_text, anchor="w", font=ctk.CTkFont(size=11))
        self.status_bar.pack(fill="x", padx=12, pady=(0, 6))

    # ==================== SEARCH ====================
    # Updates search query when user types and refreshes the table
    def on_search(self, event=None):
        self.search_query = self.search_entry.get().lower().strip()
        self.current_page = 1
        self.populate_table()
    # Clears the search box and resets the table
    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.search_query = ""
        self.current_page = 1
        self.populate_table()

    # ==================== PAGINATION ====================
    # Changes how many items per page and refreshes
    def change_items_per_page(self, value):
        self.items_per_page = int(value)
        self.current_page = 1
        self.populate_table()
    # Navigates between pages
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.populate_table()
    def next_page(self):
        total_pages = self.get_total_pages()
        if self.current_page < total_pages:
            self.current_page += 1
            self.populate_table()
    # Goes to specific page when user types number and presses Enter
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
    # Calculates how many pages exist based on current filters
    def get_total_pages(self):
        items = self.get_filtered_items()
        if not items:
            return 1
        return max(1, (len(items) + self.items_per_page - 1) // self.items_per_page)
    # Applies all filters (search, favorites only, hide members, hidden items) and returns the list to show
    def get_filtered_items(self):
        items = self.all_items

        if self.search_query:
            items = [item for item in items if self.search_query in item[1].get("name", "").lower()]

        if self.show_favorites_only:
            items = [item for item in items if self.item_tags.get(item[0]) == "fav"]

        if self.hide_members:
            items = [item for item in items if not item[1].get("members", False)]

        items = [item for item in items if self.item_tags.get(item[0]) != "hidden"]
        return items

    def update_pagination_ui(self):
        total_pages = self.get_total_pages()
        self.page_label.configure(text=f"/ {total_pages}")
        self.page_entry.delete(0, "end")
        self.page_entry.insert(0, str(self.current_page))
        self.total_label.configure(text=f"Total items: {len(self.get_filtered_items())}")

        self.prev_btn.configure(state="normal" if self.current_page > 1 else "disabled")
        self.next_btn.configure(state="normal" if self.current_page < total_pages else "disabled")

    # ==================== DATA HANDLING ====================
    # Loads all item data from APIs on startup and starts fast sync
    def load_initial_data(self):
        self.status_bar.configure(text="Loading data from API (with cache)...")
        self.mapping_data = api.fetch_mapping() or {}
        self.latest_data = api.fetch_latest() or {}
        self.volume_data = api.fetch_24h_volume() or {}          # NEW

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

            for item_id, _ in self.all_items:
                if item_id not in self.item_tags:
                    self.item_tags[item_id] = ""

            self.status_bar.configure(text=f"Loaded {len(self.all_items)} tradeable items • Starting sync...")
            self.current_page = 1
            self.populate_table()
            self.after(1000, self.start_fast_sync)
        else:
            self.status_bar.configure(text="Failed to load data from API")
    # Manually refreshes prices and volume data
    def refresh_prices(self):
        self.status_bar.configure(text="Refreshing prices...")
        self.latest_data = api.fetch_latest() or {}
        self.volume_data = api.fetch_24h_volume() or {}          # NEW
        self.populate_table()
        self.status_bar.configure(text="Prices refreshed • Auto-refresh: Active")
    # Clears and rebuilds the entire table with current data and calculations
    def populate_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        items_to_show = self.get_filtered_items()
        if not items_to_show:
            return

        # Usar precio efectivo (Data Logger > manual/API)
        if self.settings.get("runelite_sync_enabled", False):
            nature_cost = self.get_effective_buy_price(561) or int(self.settings["nature_price"]) if self.settings["nature_price"].isdigit() else 0
            fire_cost = self.get_effective_buy_price(554) or int(self.settings["fire_price"]) if self.settings["fire_price"].isdigit() else 0
        else:
            nature_cost = int(self.settings["nature_price"]) if self.settings["nature_price"].isdigit() else 0
            fire_cost = int(self.settings["fire_price"]) if self.settings["fire_price"].isdigit() else 0

        rune_cost = nature_cost + fire_cost if self.settings["fire_method"] == "pay" else nature_cost
        price_type = self.settings["price_type"]
        volume_type = self.settings.get("volume_type", "both")

        start = (self.current_page - 1) * self.items_per_page
        end = start + self.items_per_page
        page_items = items_to_show[start:end]

        for item_id, item in page_items:
            name = item.get("name", "Unknown")
            high_alch = item.get("highalch", 0)
            buy_limit = item.get("limit", 0) or 0
            is_members = item.get("members", False)

            effective_price = self.get_effective_buy_price(item_id)

            is_from_runelite = (
                self.settings.get("runelite_sync_enabled", False) and
                hasattr(self, "runelite_data") and
                item_id in self.runelite_data and
                self.runelite_data[item_id].get("last_buy_price")
            )
            display_ge_price = f"{effective_price}*" if is_from_runelite else effective_price
            profit = high_alch - effective_price - rune_cost
            total_profit = profit * buy_limit if buy_limit else 0
            total_investment = effective_price * buy_limit if buy_limit else 0
            daily_volume = api.get_item_volume(self.volume_data, item_id, volume_type)

            tag = self.item_tags.get(item_id, "")
            fav_display = "★" if tag == "fav" else "☆"
            members_display = "★" if is_members else ""

            # Color según progreso de compra (RuneLite)
            bought_4h = self.get_bought_last_4h(item_id)
            buy_limit = item.get("limit", 0) or 0

            if isinstance(bought_4h, int) and buy_limit > 0:
                progress = bought_4h / buy_limit
                if progress >= 1.0:
                    row_tag = "sold_out"
                elif progress >= 0.7:
                    row_tag = "almost_full"
                else:
                    row_tag = ""
            else:
                row_tag = ""

            self.tree.insert("", "end", values=(
                fav_display, members_display, name, high_alch, display_ge_price, profit, 
                total_profit, total_investment, daily_volume, bought_4h, buy_limit
            ), tags=(str(item_id), row_tag))

        self.update_pagination_ui()
    # Sorts the whole list when user clicks any column header
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
                effective_price = api.get_item_price(self.latest_data, item_id, price_type) or 0
                nature_cost = int(self.settings["nature_price"]) if self.settings["nature_price"].isdigit() else 0
                fire_cost = int(self.settings["fire_price"]) if self.settings["fire_price"].isdigit() else 0
                rune_cost = nature_cost + fire_cost if self.settings["fire_method"] == "pay" else nature_cost

                profit = data.get("highalch", 0) - effective_price - rune_cost
                buy_limit = data.get("limit", 0) or 0

                if col == "effective_price":
                    return effective_price
                elif col == "profit":
                    return profit
                elif col == "total_profit":
                    return profit * buy_limit
                elif col == "total_investment":
                    return effective_price * buy_limit
                elif col == "daily_volume":
                    volume_type = self.settings.get("volume_type", "both")
                    return api.get_item_volume(self.volume_data, item_id, volume_type)
                elif col == "bought_4h":
                    return self.get_bought_last_4h(item_id)
                return 0

        self.all_items.sort(key=get_sort_value, reverse=reverse)
        self.current_page = 1
        self.populate_table()

    # ==================== TAG SYSTEM ====================
    # Changes favorite or hidden status of an item and saves it
    def set_item_tag(self, item_id, tag):
        self.item_tags[item_id] = tag
        self.save_config()
        self.populate_table()
    # Turns Favorites Only mode on/off
    def toggle_favorites_filter(self):
        self.show_favorites_only = self.fav_only_var.get()
        self.current_page = 1
        self.populate_table()
    # Turns Hide Members filter on/off
    def toggle_hide_members(self):
        self.hide_members = not self.hide_members
        self.current_page = 1
        self.populate_table()
    # Removes all favorites
    def clear_all_favorites(self):
        for item_id in list(self.item_tags.keys()):
            if self.item_tags[item_id] == "fav":
                self.item_tags[item_id] = ""
        self.save_config()
        self.populate_table()
        self.status_bar.configure(text="All favorites cleared")
    # Permanently unhides all hidden items
    def show_hidden_items(self):
        hidden_count = 0
        for item_id in list(self.item_tags.keys()):
            if self.item_tags.get(item_id) == "hidden":
                self.item_tags[item_id] = ""
                hidden_count += 1

        if hidden_count == 0:
            self.status_bar.configure(text="No hidden items")
        else:
            self.populate_table()
            self.status_bar.configure(text=f"Unhid {hidden_count} items")

    # ======================= RUNELITE DATA ======================
    # Checks if RuneLite Data Logger folder exists and lists available accounts
    def detect_runelite_data_logger(self):
        """Check if Data Logger folder exists and return list of accounts"""
        base_path = os.path.expanduser("~/.runelite/data-logger/grand-exchange/")
        
        if not os.path.exists(base_path):
            return [], False  # No folder found
        
        try:
            accounts = [f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))]
            return accounts, True
        except:
            return [], True  # Folder exists but error reading
    # Handles enabling/disabling the RuneLite sync and updates status
    def update_runelite_sync(self):
        # Safety check - variable might not exist yet on startup
        if not hasattr(self, "runelite_sync_var"):
            return

        enabled = self.runelite_sync_var.get()
        self.settings["runelite_sync_enabled"] = enabled

        # Clear previous widgets in the account frame
        if hasattr(self, "runelite_account_frame"):
            for widget in self.runelite_account_frame.winfo_children():
                widget.destroy()

        if enabled:
            accounts, folder_exists = self.detect_runelite_data_logger()
            self.runelite_accounts = accounts

            if not folder_exists:
                if hasattr(self, "runelite_status_label"):
                    self.runelite_status_label.configure(text="Data Logger plugin not found", text_color="red")
            elif len(accounts) == 0:
                if hasattr(self, "runelite_status_label"):
                    self.runelite_status_label.configure(
                        text="Account(s) not found, buy something from the GE and try again.", 
                        text_color="red"
                    )
            else:
                current_account = self.settings.get("runelite_account", "")

                if current_account:
                    if hasattr(self, "runelite_status_label"):
                        self.runelite_status_label.configure(
                            text=f"Linked to: {current_account}", 
                            text_color="#00FF00"
                        )
                    self.load_runelite_data()
                    # Programar refresco automático cada 45 segundos mientras esté activado
                    if not hasattr(self, "_runelite_refresh_job"):
                        self._runelite_refresh_job = self.after(10000, self._periodic_runelite_refresh)

                    if hasattr(self, "runelite_account_frame"):
                        change_label = ctk.CTkLabel(self.runelite_account_frame, text="Change Account:")
                        change_label.pack(side="left", padx=(0, 5))

                        self.account_var = ctk.StringVar(value=current_account)
                        account_menu = ctk.CTkOptionMenu(
                            self.runelite_account_frame,
                            values=accounts,
                            variable=self.account_var,
                            width=140,
                            command=self.change_runelite_account
                        )
                        account_menu.pack(side="left")
                else:
                    if hasattr(self, "runelite_status_label"):
                        self.runelite_status_label.configure(text="Select your OSRS account:", text_color="white")

                    if hasattr(self, "runelite_account_frame"):
                        self.account_var = ctk.StringVar(value=accounts[0] if accounts else "")
                        account_menu = ctk.CTkOptionMenu(
                            self.runelite_account_frame,
                            values=accounts,
                            variable=self.account_var,
                            width=160,
                            command=self.select_runelite_account
                        )
                        account_menu.pack(side="left")
        else:
            if hasattr(self, "runelite_status_label"):
                self.runelite_status_label.configure(text="")

        # Actualizar status bar en tiempo real
        if hasattr(self, "status_bar"):
            account = self.settings.get("runelite_account", "")
            if enabled and account:
                self.status_bar.configure(text=f"Auto-refresh: Active  •  RuneLite: {account}")
            else:
                self.status_bar.configure(text="Auto-refresh: Active")

        self.save_config()
        self.populate_table()
    # Shows a dropdown to choose your account
    def select_runelite_account(self, selected_account):
        self.settings["runelite_account"] = selected_account
        self.save_config()
        self.update_runelite_sync()   # Refresh the UI
    # After choosing → it saves it and shows “Linked to: YourAccount”
    def change_runelite_account(self, selected_account):
        self.settings["runelite_account"] = selected_account
        self.save_config()
        self.update_runelite_sync()   # Refresh the UI
    # Load Data Logger data for the selected account
    def load_runelite_data(self):
        """Load Data Logger data with 4h window + last buy price per item"""
        account = self.settings.get("runelite_account", "")
        if not account:
            return

        base_path = os.path.expanduser(f"~/.runelite/data-logger/grand-exchange/{account}/")

        if not os.path.exists(base_path):
            print(f"[RuneLite] Folder not found for account: {account}")
            return

        try:
            json_files = [f for f in os.listdir(base_path) if f.endswith(".json")]
            if not json_files:
                print("[RuneLite] No JSON files found")
                return

            json_path = os.path.join(base_path, json_files[0])
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)

            self.runelite_data = {}
            four_hours_ms = 4 * 60 * 60 * 1000

            # 1. Agrupar todas las compras por item_id
            purchases_by_item = {}
            for entry in raw_data:
                if not entry.get("isBuy"):
                    continue
                item_id = entry.get("itemId")
                if not item_id:
                    continue
                if item_id not in purchases_by_item:
                    purchases_by_item[item_id] = []
                purchases_by_item[item_id].append({
                    "time": entry.get("offerCreationTime", 0),
                    "quantity": entry.get("quantity", 0),
                    "price": entry.get("price", 0)
                })

            # 2. Calcular bought_last_4h + last_buy_price para cada item
            for item_id, purchases in purchases_by_item.items():
                purchases.sort(key=lambda x: x["time"])

                # Calcular bought_last_4h (ventana deslizante)
                bought = 0
                left = 0
                for right in range(len(purchases)):
                    while purchases[right]["time"] - purchases[left]["time"] > four_hours_ms:
                        left += 1
                    current_sum = sum(p["quantity"] for p in purchases[left:right+1])
                    bought = max(bought, current_sum)

                # Guardar precio más reciente de compra
                latest_price = purchases[-1]["price"] if purchases else 0

                self.runelite_data[item_id] = {
                    "bought_last_4h": bought,
                    "last_buy_price": latest_price
                }

            # 3. Extraer precios recientes de Nature y Fire runes (para auto-fill)
            self.last_nature_price = None
            self.last_fire_price = None

            for entry in raw_data:
                if not entry.get("isBuy"):
                    continue
                item_id = entry.get("itemId")
                price = entry.get("price", 0)

                if item_id == 561 and self.last_nature_price is None:
                    self.last_nature_price = price
                elif item_id == 554 and self.last_fire_price is None:
                    self.last_fire_price = price

            print(f"[RuneLite] Loaded 4h sliding window data for {len(self.runelite_data)} items")
            self.populate_table()

        except Exception as e:
            print(f"[RuneLite] Error loading data: {e}")

    def refresh_runelite_data(self):
        """Recarga los datos de RuneLite y actualiza la tabla (para actualizaciones en tiempo real)"""
        if not self.settings.get("runelite_sync_enabled", False):
            return

        account = self.settings.get("runelite_account", "")
        if not account:
            return

        # Solo recargar si ya teníamos datos cargados
        if hasattr(self, "runelite_data") and self.runelite_data:
            self.load_runelite_data()
            print("[RuneLite] Data refreshed (auto)")

    def _periodic_runelite_refresh(self):
        """Chequeo cada 1 segundo. Solo recarga si el archivo realmente cambió."""
        if not self.settings.get("runelite_sync_enabled", False):
            if hasattr(self, "_runelite_refresh_job"):
                del self._runelite_refresh_job
            return

        account = self.settings.get("runelite_account", "")
        if not account:
            self._runelite_refresh_job = self.after(1000, self._periodic_runelite_refresh)
            return

        base_path = os.path.expanduser(f"~/.runelite/data-logger/grand-exchange/{account}/")

        if not os.path.exists(base_path):
            self._runelite_refresh_job = self.after(1000, self._periodic_runelite_refresh)
            return

        json_files = [f for f in os.listdir(base_path) if f.endswith(".json")]
        if not json_files:
            self._runelite_refresh_job = self.after(1000, self._periodic_runelite_refresh)
            return

        json_path = os.path.join(base_path, json_files[0])

        try:
            current_mtime = os.path.getmtime(json_path)
            current_size = os.path.getsize(json_path)

            last_mtime = getattr(self, "_last_runelite_mtime", 0)
            last_size = getattr(self, "_last_runelite_size", 0)

            if current_mtime != last_mtime or current_size != last_size:
                self._last_runelite_mtime = current_mtime
                self._last_runelite_size = current_size

                self.load_runelite_data()

                if hasattr(self, "status_bar"):
                    self.status_bar.configure(text=f"Auto-refresh: Active  •  RuneLite: {account} (updated)")

            # Chequear cada 1 segundo
            self._runelite_refresh_job = self.after(1000, self._periodic_runelite_refresh)

        except Exception as e:
            print(f"[RuneLite] Error checking file: {e}")
            self._runelite_refresh_job = self.after(1000, self._periodic_runelite_refresh)

    # Returns how many of this item the user Bought (4h)
    def get_bought_last_4h(self, item_id):
        """Returns how many of this item were bought in the last 4 hours"""
        if not self.settings.get("runelite_sync_enabled", False):
            return "-"
        if not hasattr(self, "runelite_data") or not self.runelite_data:
            return 0
        return self.runelite_data.get(item_id, {}).get("bought_last_4h", 0)
    
    def get_effective_buy_price(self, item_id):
        """Devuelve el precio de compra real si existe en Data Logger, si no usa GE"""
        if self.settings.get("runelite_sync_enabled", False):
            if hasattr(self, "runelite_data") and item_id in self.runelite_data:
                price = self.runelite_data[item_id].get("last_buy_price")
                if price and price > 0:
                    return price

        # Fallback al precio GE
        price_type = self.settings.get("price_type", "average")
        return api.get_item_price(self.latest_data, item_id, price_type) or 0
    
    # Returns the most recent buy prices for Nature and Fire runes
    def get_last_rune_prices(self):
        """Returns the most recent buy prices for Nature and Fire runes"""
        return {
            "nature": self.last_nature_price,
            "fire": self.last_fire_price
        }

    # ==================== SMART AUTO-REFRESH ====================
    # Starts the fast 1-second polling on startup
    def start_fast_sync(self):
        self.fast_sync_active = True
        self.fast_sync_attempts = 0
        self.spinner_index = 0
        self.status_bar.configure(text="Syncing with latest prices... -")
        self.fast_sync_step()
    # One step of fast sync with spinner animation
    def fast_sync_step(self):
        if not self.fast_sync_active:
            return

        self.fast_sync_attempts += 1
        spinner = ['-', '\\', '|', '/'][self.spinner_index % 4]
        self.spinner_index += 1
        self.status_bar.configure(text=f"Syncing with latest prices... {spinner}")

        try:
            new_latest = api.fetch_latest()
            if new_latest and new_latest != self.latest_data:
                self.latest_data = new_latest
                self.populate_table()
                self.fast_sync_active = False
                self.status_bar.configure(text=f"Synced! • {len(self.all_items)} items • Auto-refresh: Active")
                self.after(60000, self.background_auto_refresh)
                return
        except Exception as e:
            print(f"Fast sync error: {e}")

        if self.fast_sync_attempts < self.max_fast_sync_attempts:
            self.after(1000, self.fast_sync_step)
        else:
            self.fast_sync_active = False
            self.status_bar.configure(text="Sync failed after 60s. Using cached data.")
            self.after(3000, lambda: self.status_bar.configure(
                text=f"Loaded {len(self.all_items)} tradeable items • Auto-refresh: Active"
            ))
            self.after(60000, self.background_auto_refresh)
    # Normal 60-second refresh loop
    def background_auto_refresh(self):
        if self.fast_sync_active:
            return

        try:
            new_latest = api.fetch_latest()
            if new_latest:
                self.latest_data = new_latest
                self.populate_table()
                self.status_bar.configure(text=f"Auto-refreshed • {len(self.all_items)} items • Auto-refresh: Active")
        except Exception as e:
            print(f"Auto-refresh error: {e}")

        self.after(60000, self.background_auto_refresh)

    # ==================== CONTEXT MENU ====================
    # Shows right-click menu (Favorite / Hide options)
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return

        tags = self.tree.item(item, "tags")
        if not tags:
            return

        item_id = int(tags[0])
        current_tag = self.item_tags.get(item_id, "")

        menu = Menu(self, tearoff=0)

        if current_tag == "fav":
            menu.add_command(label="Remove from Favorites", command=lambda: self.set_item_tag(item_id, ""))
        else:
            menu.add_command(label="Add to Favorites", command=lambda: self.set_item_tag(item_id, "fav"))

        if current_tag == "hidden":
            menu.add_command(label="Unhide Item", command=lambda: self.set_item_tag(item_id, ""))
        else:
            menu.add_command(label="Hide Item", command=lambda: self.set_item_tag(item_id, "hidden"))

        menu.tk_popup(event.x_root, event.y_root)

    # ==================== CONFIGURATION ====================
    # Opens and builds the full Configuration window
    def open_configuration(self):
        self.config_window = ctk.CTkToplevel(self)
        self.config_window.title("Configuration")
        self.config_window.geometry("400x760")
        self.config_window.resizable(False, False)
        self.config_window.transient(self)
        self.config_window.grab_set()

        # ==================== HEADER ====================
        ctk.CTkLabel(self.config_window, text="Configuration", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=12)

        price_type = self.settings.get("price_type", "average")
        nature_api_price = api.get_item_price(self.latest_data, 561, price_type) or 0
        fire_api_price = api.get_item_price(self.latest_data, 554, price_type) or 0

        self.price_label = ctk.CTkLabel(
            self.config_window,
            text=f"Current API Prices ({price_type.capitalize()}):   Nature: {nature_api_price} gp   |   Fire: {fire_api_price} gp",
            font=ctk.CTkFont(size=11),
            text_color="#AAAAAA"
        )
        self.price_label.pack(pady=(0, 15))

        # ==================== NATURE RUNE ====================
        ctk.CTkLabel(self.config_window, text="Nature Rune Price (gp)").pack(anchor="w", padx=25)
        nature_frame = ctk.CTkFrame(self.config_window, fg_color="transparent")
        nature_frame.pack(fill="x", padx=25, pady=3)

        self.nature_entry = ctk.CTkEntry(nature_frame)
        self.nature_entry.pack(side="left", fill="x", expand=True)

        # Auto-fill from RuneLite recent purchases if available
        nature_price = self.settings.get("nature_price", "")
        if not nature_price and self.settings.get("runelite_sync_enabled"):
            prices = self.get_last_rune_prices()
            if prices.get("nature"):
                nature_price = str(prices["nature"])

        self.nature_entry.insert(0, nature_price)
        label_text = "(from your recent purchases)" if self.settings.get("runelite_sync_enabled") and self.get_last_rune_prices().get("nature") else "(Leave empty = API)"
        ctk.CTkLabel(nature_frame, text=label_text, text_color="gray").pack(side="left", padx=6)

        save_nature_btn = ctk.CTkButton(nature_frame, text="Save", width=55,
                                        command=self.save_nature_price)
        save_nature_btn.pack(side="left", padx=6)

        # ==================== FIRE RUNE ====================
        ctk.CTkLabel(self.config_window, text="Fire Rune Method").pack(anchor="w", padx=25, pady=(10, 0))
        self.fire_method_var = ctk.StringVar(value=self.settings.get("fire_method", "staff"))

        ctk.CTkRadioButton(self.config_window, text="Use Fire Staff / Tome of Fire (Free)", 
                           variable=self.fire_method_var, value="staff",
                           command=self.update_settings_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="Pay for Fire Runes", 
                           variable=self.fire_method_var, value="pay",
                           command=self.update_settings_live).pack(anchor="w", padx=25)

        ctk.CTkLabel(self.config_window, text="Fire Rune Price (if paying)").pack(anchor="w", padx=25, pady=(8, 0))
        fire_frame = ctk.CTkFrame(self.config_window, fg_color="transparent")
        fire_frame.pack(fill="x", padx=25, pady=3)

        self.fire_entry = ctk.CTkEntry(fire_frame)
        self.fire_entry.pack(side="left", fill="x", expand=True)

        # Auto-fill from RuneLite recent purchases if available
        fire_price = self.settings.get("fire_price", "")
        if not fire_price and self.settings.get("runelite_sync_enabled"):
            prices = self.get_last_rune_prices()
            if prices.get("fire"):
                fire_price = str(prices["fire"])

        self.fire_entry.insert(0, fire_price)
        label_text = "(from your recent purchases)" if self.settings.get("runelite_sync_enabled") and self.get_last_rune_prices().get("fire") else "(Leave empty = API)"
        ctk.CTkLabel(fire_frame, text=label_text, text_color="gray").pack(side="left", padx=6)

        save_fire_btn = ctk.CTkButton(fire_frame, text="Save", width=55,
                                      command=self.save_fire_price)
        save_fire_btn.pack(side="left", padx=6)

        # ==================== GE PRICE TYPE ====================
        ctk.CTkLabel(self.config_window, text="GE Price Type").pack(anchor="w", padx=25, pady=(10, 0))
        self.price_type_var = ctk.StringVar(value=self.settings.get("price_type", "average"))

        ctk.CTkRadioButton(self.config_window, text="Low Price", variable=self.price_type_var, value="low",
                           command=self.update_price_type_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="High Price", variable=self.price_type_var, value="high",
                           command=self.update_price_type_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="Average (Recommended)", variable=self.price_type_var, value="average",
                           command=self.update_price_type_live).pack(anchor="w", padx=25)

        # ==================== GE VOLUME TYPE ====================
        ctk.CTkLabel(self.config_window, text="GE Volume Type").pack(anchor="w", padx=25, pady=(10, 0))
        self.volume_type_var = ctk.StringVar(value=self.settings.get("volume_type", "both"))

        ctk.CTkRadioButton(self.config_window, text="Low Volume", variable=self.volume_type_var, value="low",
                           command=self.update_volume_type_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="High Volume", variable=self.volume_type_var, value="high",
                           command=self.update_volume_type_live).pack(anchor="w", padx=25)
        ctk.CTkRadioButton(self.config_window, text="Both (Recommended)", variable=self.volume_type_var, value="both",
                           command=self.update_volume_type_live).pack(anchor="w", padx=25)

        # ==================== RUNELITE PLUGINS SUPPORT ====================
        ctk.CTkLabel(self.config_window, text="").pack(pady=5)  # Spacer

        separator = ctk.CTkFrame(self.config_window, height=2, fg_color="#444444")
        separator.pack(fill="x", padx=20, pady=8)

        ctk.CTkLabel(self.config_window, text="RuneLite Plugins Support", 
                     font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=25, pady=(5, 8))

        # RuneLite Sync Toggle
        self.runelite_sync_var = ctk.BooleanVar(value=self.settings.get("runelite_sync_enabled", False))
        runelite_toggle = ctk.CTkCheckBox(
            self.config_window, 
            text="Sync with RuneLite Data Logger",
            variable=self.runelite_sync_var,
            command=self.update_runelite_sync
        )
        runelite_toggle.pack(anchor="w", padx=25)

        ctk.CTkLabel(self.config_window, 
                     text="(Reads your Grand Exchange activity for buy limits and suggestions)",
                     font=ctk.CTkFont(size=10), text_color="gray").pack(anchor="w", padx=45)

        # Status / Account selection area
        self.runelite_status_label = ctk.CTkLabel(self.config_window, text="", font=ctk.CTkFont(size=11))
        self.runelite_status_label.pack(anchor="w", padx=25, pady=(8, 0))

        # This is where we will dynamically add the account dropdown later
        self.runelite_account_frame = ctk.CTkFrame(self.config_window, fg_color="transparent")
        self.runelite_account_frame.pack(fill="x", padx=25, pady=5)

        # Initialize RuneLite section status when opening the window
        if hasattr(self, "runelite_sync_var"):
            self.update_runelite_sync()

    # Live update when changing options
    def update_settings_live(self):
        self.settings["fire_method"] = self.fire_method_var.get()
        self.save_config()
        self.populate_table()
    def update_price_type_live(self):
        self.settings["price_type"] = self.price_type_var.get()
        self.save_config()
        self.populate_table()
        price_type = self.settings["price_type"]
        nature_api_price = api.get_item_price(self.latest_data, 561, price_type) or 0
        fire_api_price = api.get_item_price(self.latest_data, 554, price_type) or 0
        self.price_label.configure(
            text=f"Current API Prices ({price_type.capitalize()}):   Nature: {nature_api_price} gp   |   Fire: {fire_api_price} gp"
        )
    def update_volume_type_live(self):
        self.settings["volume_type"] = self.volume_type_var.get()
        self.save_config()
        self.populate_table()

    # Save specific rune prices
    def save_nature_price(self):
        self.settings["nature_price"] = self.nature_entry.get().strip()
        self.save_config()
        self.populate_table()
    def save_fire_price(self):
        self.settings["fire_price"] = self.fire_entry.get().strip()
        self.save_config()
        self.populate_table()


if __name__ == "__main__":
    app = SimpleAlchApp()
    app.mainloop()