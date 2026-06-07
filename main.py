import customtkinter as ctk

class SimpleAlchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SimpleAlch - OSRS High Alchemy Tool")
        self.geometry("1280x720")
        self.minsize(1100, 650)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Store current settings
        self.settings = {
            "nature_price": "",
            "fire_method": "staff",      # "staff" or "pay"
            "fire_price": "",
            "price_type": "average",     # "low", "high", "average"
        }

        self._create_top_bar()
        self._create_main_area()
        self._create_status_bar()

    def _create_top_bar(self):
        self.top_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.top_bar.pack(fill="x")

        title_label = ctk.CTkLabel(
            self.top_bar, text="SimpleAlch", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        self.refresh_btn = ctk.CTkButton(
            self.top_bar, text="Refresh Prices", width=120,
            command=self.refresh_prices
        )
        self.refresh_btn.pack(side="right", padx=10, pady=8)

        self.config_btn = ctk.CTkButton(
            self.top_bar, text="⚙ Configuration", width=140,
            command=self.open_configuration
        )
        self.config_btn.pack(side="right", padx=10, pady=8)

    def _create_main_area(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=8)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        placeholder = ctk.CTkLabel(
            self.main_frame, 
            text="Main Table Area\n(Profitable items will appear here)", 
            font=ctk.CTkFont(size=16), text_color="gray"
        )
        placeholder.pack(expand=True)

    def _create_status_bar(self):
        self.status_bar = ctk.CTkLabel(
            self, text="Ready • Last updated: Never", 
            anchor="w", font=ctk.CTkFont(size=12)
        )
        self.status_bar.pack(fill="x", padx=15, pady=(0, 8))

    # ==================== ACTIONS ====================
    def refresh_prices(self):
        self.status_bar.configure(text="Refreshing prices...")
        self.after(800, lambda: self.status_bar.configure(text="Prices updated"))

    def open_configuration(self):
        config_window = ctk.CTkToplevel(self)
        config_window.title("Configuration")
        config_window.geometry("560x520")
        config_window.resizable(False, False)
        config_window.transient(self)
        config_window.grab_set()

        # Title
        ctk.CTkLabel(config_window, text="Configuration", 
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(15, 10))

        # === Nature Rune ===
        ctk.CTkLabel(config_window, text="Nature Rune Price (gp)", 
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=30)
        
        nature_frame = ctk.CTkFrame(config_window, fg_color="transparent")
        nature_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        self.nature_entry = ctk.CTkEntry(nature_frame, placeholder_text="Leave empty for API price")
        self.nature_entry.pack(side="left", fill="x", expand=True)
        self.nature_entry.insert(0, self.settings.get("nature_price", ""))
        
        ctk.CTkLabel(nature_frame, text="(API Avg: 124 gp)", 
                     text_color="gray").pack(side="left", padx=8)

        # === Fire Rune Method ===
        ctk.CTkLabel(config_window, text="Fire Rune Method", 
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=30)
        
        self.fire_method_var = ctk.StringVar(value=self.settings.get("fire_method", "staff"))
        
        fire_frame = ctk.CTkFrame(config_window, fg_color="transparent")
        fire_frame.pack(fill="x", padx=30, pady=(5, 10))
        
        ctk.CTkRadioButton(fire_frame, text="Use Fire Staff / Tome of Fire (0 gp)", 
                           variable=self.fire_method_var, value="staff").pack(anchor="w")
        ctk.CTkRadioButton(fire_frame, text="Pay for Fire Runes", 
                           variable=self.fire_method_var, value="pay").pack(anchor="w")

        # === Fire Rune Price (only shown when "pay" is selected) ===
        ctk.CTkLabel(config_window, text="Fire Rune Price (gp)", 
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=30)
        
        fire_price_frame = ctk.CTkFrame(config_window, fg_color="transparent")
        fire_price_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        self.fire_entry = ctk.CTkEntry(fire_price_frame, placeholder_text="Leave empty for API price")
        self.fire_entry.pack(side="left", fill="x", expand=True)
        self.fire_entry.insert(0, self.settings.get("fire_price", ""))
        
        ctk.CTkLabel(fire_price_frame, text="(API Avg: 5 gp)", 
                     text_color="gray").pack(side="left", padx=8)

        # === GE Price Type ===
        ctk.CTkLabel(config_window, text="GE Price Type for Calculations", 
                     font=ctk.CTkFont(size=13)).pack(anchor="w", padx=30)
        
        self.price_type_var = ctk.StringVar(value=self.settings.get("price_type", "average"))
        
        price_frame = ctk.CTkFrame(config_window, fg_color="transparent")
        price_frame.pack(fill="x", padx=30, pady=5)
        
        ctk.CTkRadioButton(price_frame, text="Low Price", 
                           variable=self.price_type_var, value="low").pack(anchor="w")
        ctk.CTkRadioButton(price_frame, text="High Price", 
                           variable=self.price_type_var, value="high").pack(anchor="w")
        ctk.CTkRadioButton(price_frame, text="Average (Recommended)", 
                           variable=self.price_type_var, value="average").pack(anchor="w")

        # Save Button
        save_btn = ctk.CTkButton(
            config_window, text="Save Settings", 
            command=lambda: self.save_settings(config_window)
        )
        save_btn.pack(pady=20)

    def save_settings(self, window):
        self.settings["nature_price"] = self.nature_entry.get().strip()
        self.settings["fire_method"] = self.fire_method_var.get()
        self.settings["fire_price"] = self.fire_entry.get().strip()
        self.settings["price_type"] = self.price_type_var.get()
        
        print("Settings saved:", self.settings)  # For debugging
        window.destroy()


if __name__ == "__main__":
    app = SimpleAlchApp()
    app.mainloop()