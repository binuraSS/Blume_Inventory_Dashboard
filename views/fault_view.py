import customtkinter as ctk
import threading
from styles import *
from data.repairs import report_fault

class FaultReportView(ctk.CTkFrame):
    def __init__(self, master, show_msg_callback):
        # Fill the whole view with the window background color
        super().__init__(master, fg_color=G_WINDOW_BG, corner_radius=0)
        self.show_msg = show_msg_callback
        
        # --- 1. Page Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=30)
        
        ctk.CTkLabel(
            header, 
            text="Report Device Fault", 
            font=FONT_H1, 
            text_color=G_TEXT
        ).pack(side="left")

        # --- 2. Centered Form Card ---
        # Using G_BG so this card turns dark grey in Night Mode
        card = ctk.CTkFrame(self, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(pady=40, padx=30)

        container = ctk.CTkFrame(card, fg_color="transparent")
        container.pack(padx=60, pady=40)

        self.bid = create_material_input(container, "Device Blume ID", "Enter ID")
        self.status = create_material_dropdown(container, "Device Status", ["Physical damage", "Tracking error", "Software Error"])
        
        ctk.CTkLabel(container, text="  Issue Notes", font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        
        # Textbox specifically needs adaptive colors to avoid "black on black" in Night Mode
        self.notes = ctk.CTkTextbox(
            container, 
            width=400, 
            height=120, 
            border_color=G_BORDER, 
            border_width=2, 
            corner_radius=8,
            fg_color=G_WINDOW_BG, # Slightly different shade for input areas
            text_color=G_TEXT
        )
        self.notes.pack(pady=5)

        btn = ctk.CTkButton(container, text="Log Fault", command=self.handle_submit)
        apply_material_button(btn, "primary")
        btn.pack(pady=40)

    def handle_submit(self):
        # Gather data from UI before starting thread
        blume_id = self.bid.get()
        status_val = self.status.get()
        notes_val = self.notes.get("1.0", "end-1c")

        if not blume_id.strip():
            self.show_msg("Error: Blume ID is required")
            return

        def task():
            try:
                tid = report_fault(blume_id, status_val, notes_val)
                # Update UI on main thread
                self.after(0, lambda: self.show_msg(f"Fault Logged: {tid}"))
                self.after(0, self._clear_inputs)
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda err=error_msg: self.show_msg(f"Error: {err}"))
        
        threading.Thread(target=task, daemon=True).start()

    def _clear_inputs(self):
        """Reset the form after successful submission."""
        self.bid.delete(0, 'end')
        self.notes.delete("1.0", 'end')