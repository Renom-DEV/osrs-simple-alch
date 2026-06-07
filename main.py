import customtkinter as ctk

class SimpleAlchApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SimpleAlch - OSRS High Alchemy Tool")
        self.geometry("1280x720")
        self.minsize(1100, 650)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # ==================== TOP BAR ====================
        self.top_bar = ctk.CTkFrame(self, height=50, corner_radius=0)
        self.top_bar.pack(fill="x", padx=0, pady=0)

        # Title
        title_label = ctk.CTkLabel(
            self.top_bar, 
            text="SimpleAlch", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=20)

        # Refresh Button
        self.refresh_btn = ctk.CTkButton(
            self.top_bar, 
            text="Refresh Prices", 
            width=120,
            command=self.refresh_prices
        )
        self.refresh_btn.pack(side="right", padx=10, pady=8)

        # Configuration Button
        self.config_btn = ctk.CTkButton(
            self.top_bar, 
            text="⚙ Configuration", 
            width=140,
            command=self.open_configuration
        )
        self.config_btn.pack(side="right", padx=10, pady=8)

        # ==================== MAIN CONTENT AREA ====================
        self.main_frame = ctk.CTkFrame(self, corner_radius=8)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Placeholder for the future table
        placeholder = ctk.CTkLabel(
            self.main_frame, 
            text="Main Table Area\n\n(This will contain the list of profitable items)", 
            font=ctk.CTkFont(size=16),
            text_color="gray"
        )
        placeholder.pack(expand=True)

        # ==================== STATUS BAR ====================
        self.status_bar = ctk.CTkLabel(
            self, 
            text="Ready • Last updated: Never", 
            anchor="w",
            font=ctk.CTkFont(size=12)
        )
        self.status_bar.pack(fill="x", padx=15, pady=(0, 8))

    # ==================== FUNCTIONS ====================
    def refresh_prices(self):
        """Placeholder for refresh functionality"""
        self.status_bar.configure(text="Refreshing prices from API...")
        self.after(1000, lambda: self.status_bar.configure(text="Prices updated successfully"))

    def open_configuration(self):
        """Open Configuration as a proper modal dialog"""
        config_window = ctk.CTkToplevel(self)
        config_window.title("Configuration")
        config_window.geometry("520x450")
        config_window.resizable(False, False)

        # Correct behavior - appears above main window but acts normally
        config_window.transient(self)     # Attach to main window
        config_window.grab_set()          # Make it modal

        label = ctk.CTkLabel(
            config_window, 
            text="Configuration Panel\n\nThis is where you will set:\n• Nature Rune cost\n• Fire Rune method & cost\n• GE Price type (Low/High/Average)\n• Auto-refresh settings", 
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        label.pack(pady=30, padx=30)

        close_btn = ctk.CTkButton(
            config_window, 
            text="Close", 
            command=config_window.destroy
        )
        close_btn.pack(pady=20)


if __name__ == "__main__":
    app = SimpleAlchApp()
    app.mainloop()