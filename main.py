import customtkinter as ctk

class SimpleAlchApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("SimpleAlch - OSRS High Alchemy Tool")
        self.geometry("1200x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        label = ctk.CTkLabel(self, text="SimpleAlch initialized successfully!", font=("Segoe UI", 20))
        label.pack(pady=50)

if __name__ == "__main__":
    app = SimpleAlchApp()
    app.mainloop()