import customtkinter as ctk
from datetime import datetime
import threading
from styles import *
from data.inventory import add_device

class AddDeviceView(ctk.CTkFrame):
    def __init__(self, master, show_msg_callback):
        # Match the window background
        super().__init__(master, fg_color=G_WINDOW_BG, corner_radius=0)
        self.show_msg = show_msg_callback
        
        # --- 1. Page Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=30)
        
        ctk.CTkLabel(header, text="Add New Resource", font=FONT_H1, text_color=G_TEXT).pack(side="left")

        # --- 2. Form Card ---
        # Centering the form inside a Material-style card
        card = ctk.CTkFrame(self, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(pady=40, padx=30)

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(padx=60, pady=40)

        self.bid = create_material_input(container, "Blume ID", "B-1234")
        self.cat = create_material_dropdown(container, "Category", ["VR Headset", "Battery Pack", "Remote"])
        self.sn = create_material_input(container, "Serial Number", "SN-XXXX")
        self.date = create_material_input(container, "Date", "YYYY-MM-DD")
        self.date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        btn = ctk.CTkButton(container, text="Create Resource", command=self.handle_submit)
        apply_material_button(btn, "primary")
        btn.pack(pady=40)

    def handle_submit(self):
        def task():
            try:
                add_device(self.bid.get(), self.cat.get(), self.sn.get(), self.date.get())
                self.after(0, lambda: self.show_msg("Device Added Successfully"))
            except Exception as e:
                err_msg = str(e)
                self.after(0, lambda m=err_msg: self.show_msg(f"Error: {m}"))
        threading.Thread(target=task, daemon=True).start()