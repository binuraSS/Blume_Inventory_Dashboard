import customtkinter as ctk
from datetime import datetime
import threading
import database
from styles import *

class AddDeviceView(ctk.CTkFrame):
    def __init__(self, master, show_msg_callback):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        self.show_msg = show_msg_callback
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=60, expand=True)

        self.bid = create_material_input(container, "Blume ID", "B-1234")
        self.cat = create_material_dropdown(container, "Category", ["VR Headset", "Battery Pack", "Remote L", "Remote R"])
        self.sn = create_material_input(container, "Serial Number", "SN-XXXX")
        self.date = create_material_input(container, "Date", "YYYY-MM-DD")
        self.date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        btn = ctk.CTkButton(container, text="Create Resource", command=self.handle_submit)
        apply_material_button(btn, "primary")
        btn.pack(pady=40)

    def handle_submit(self):
        def task():
            try:
                database.add_device(self.bid.get(), self.cat.get(), self.sn.get(), self.date.get())
                self.after(0, lambda: self.show_msg("Device Added Successfully"))
            except Exception as e:
                self.after(0, lambda: self.show_msg(f"Error: {str(e)}"))
        threading.Thread(target=task, daemon=True).start()