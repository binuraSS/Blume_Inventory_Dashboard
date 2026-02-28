import customtkinter as ctk
import threading
import database
from styles import *

class FaultReportView(ctk.CTkFrame):
    def __init__(self, master, show_msg_callback):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        self.show_msg = show_msg_callback
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(pady=60, expand=True)

        self.bid = create_material_input(container, "Device Blume ID", "Enter ID")
        self.status = create_material_dropdown(container, "Device Status", ["Physical damage", "Tracking error", "Software Error"])
        
        ctk.CTkLabel(container, text="  Issue Notes", font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        self.notes = ctk.CTkTextbox(container, width=400, height=120, border_color=G_BORDER, border_width=2, corner_radius=8)
        self.notes.pack(pady=5)

        btn = ctk.CTkButton(container, text="Log Fault", command=self.handle_submit)
        apply_material_button(btn, "primary")
        btn.pack(pady=40)

    def handle_submit(self):
        def task():
            try:
                tid = database.report_fault(self.bid.get(), self.status.get(), self.notes.get("1.0", "end-1c"))
                self.after(0, lambda: self.show_msg(f"Fault Logged: {tid}"))
            except Exception as e:
                self.after(0, lambda err=e: self.show_msg(f"Error: {str(err)}"))
        threading.Thread(target=task, daemon=True).start()