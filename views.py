# views.py
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
        self.cat = create_material_dropdown(container, "Category", ["VR Headset (HTC Vive)", "External Battery Pack", "Left Hand Remote", "Right Hand Remote"])
        self.sn = create_material_input(container, "Serial Number", "SN-XXXX-XXXX")
        self.date = create_material_input(container, "Date", "YYYY-MM-DD")
        self.date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        self.btn = ctk.CTkButton(container, text="Create Resource", command=self.handle_submit)
        apply_material_button(self.btn, "primary")
        self.btn.pack(pady=40)

    def handle_submit(self):
        def task():
            try:
                database.add_device(self.bid.get(), self.cat.get(), self.sn.get(), self.date.get())
                self.master.after(0, lambda: self.show_msg("Device Added Successfully"))
            except Exception as e:
                self.master.after(0, lambda: self.show_msg(f"Error: {str(e)}"))
        threading.Thread(target=task, daemon=True).start()

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

        self.btn = ctk.CTkButton(container, text="Log Fault", command=self.handle_submit)
        apply_material_button(self.btn, "primary") # Use "primary" or add an "error" variant to styles
        self.btn.pack(pady=40)

    def handle_submit(self):
        def task():
            try:
                tid = database.report_fault(self.bid.get(), self.status.get(), self.notes.get("1.0", "end-1c"))
                self.master.after(0, lambda: self.show_msg(f"Fault Logged: {tid}"))
            except Exception as e:
                self.master.after(0, lambda: self.show_msg(f"Error: {str(e)}"))
        threading.Thread(target=task, daemon=True).start()

class SearchView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        p = ctk.CTkFrame(self, fg_color="transparent")
        p.pack(fill="both", expand=True, padx=20, pady=20)
        
        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))
        
        self.entry = ctk.CTkEntry(bar, placeholder_text="Search ID or Status...", width=400, height=40, corner_radius=20)
        self.entry.pack(side="left", padx=10)
        
        s_btn = ctk.CTkButton(bar, text="Search", width=100, command=self.run_search)
        apply_material_button(s_btn, "primary")
        s_btn.pack(side="left")

        self.res_area = ctk.CTkScrollableFrame(p, fg_color=G_WINDOW_BG, corner_radius=8)
        self.res_area.pack(fill="both", expand=True)

    def run_search(self):
        for w in self.res_area.winfo_children(): w.destroy()
        results = database.search_device(self.entry.get())
        if not results:
            ctk.CTkLabel(self.res_area, text="No matches found.", font=FONT_BODY).pack(pady=20)
            return

        for item in results:
            issues = item.get('issues', [])
            if not issues:
                self.create_card(item, None)
            else:
                for issue in issues:
                    self.create_card(item, issue)

    def create_card(self, item, issue):
        card = ctk.CTkFrame(self.res_area, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(fill="x", pady=8, padx=15)
        
        # Color Accent
        accent_color = G_RED if issue else G_BLUE
        accent = ctk.CTkFrame(card, width=6, fg_color=accent_color, corner_radius=0)
        accent.pack(side="left", fill="y")
        
        cont = ctk.CTkFrame(card, fg_color="transparent")
        cont.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        # --- 1. Header Section ---
# --- Material Header with Multi-Color Labels ---
        header_frame = ctk.CTkFrame(cont, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 12))

        def add_header_item(parent, label, value, show_separator=False):
            """Internal helper to style the header labels differently from values."""
            if show_separator:
                ctk.CTkLabel(parent, text="  •  ", font=FONT_H2, text_color=G_BORDER).pack(side="left")
            
            # The Label (Subtle Color)
            ctk.CTkLabel(parent, text=f"{label}: ", font=("Segoe UI", 18), text_color=G_SUBTEXT).pack(side="left")
            # The Value (Bold & High Contrast)
            ctk.CTkLabel(parent, text=value, font=("Segoe UI", 18, "bold"), text_color=G_TEXT).pack(side="left")

        if issue:
            # Format: Ticket ID: ID-0000X  •  Blume ID: B-1234
            add_header_item(header_frame, "Ticket ID", issue['Ticket ID'])
            add_header_item(header_frame, "Blume ID", item['Blume ID'], show_separator=True)
        else:
            # Format: Blume ID: B-1234
            add_header_item(header_frame, "Blume ID", item['Blume ID'])

        # Hairline separator for Material structure
        ctk.CTkFrame(cont, height=1, fg_color=G_BORDER).pack(fill="x", pady=(0, 10))
        # Date badge on the right
        reg_date = issue['Issue Date'] if issue else item['Originated Date']
        date_label = "Logged:" if issue else "Registered:"
        ctk.CTkLabel(header_frame, text=f"{date_label} {reg_date}", font=FONT_BODY, text_color=G_SUBTEXT).pack(side="right")

        # --- 2. Information Grid ---
        info_frame = ctk.CTkFrame(cont, fg_color="transparent")
        info_frame.pack(fill="x", pady=5)

        # Field: Category
        self._add_field(info_frame, "Category:", item['Item Category'], 0)
        # Field: Serial Number
        self._add_field(info_frame, "Serial Number:", item['Serial Number'], 1)

        # --- 3. Fault Details (Only if issue exists) ---
        if issue:
            ctk.CTkFrame(cont, height=1, fg_color=G_BORDER).pack(fill="x", pady=10)
            
            # Fault Status
            status_frame = ctk.CTkFrame(cont, fg_color="transparent")
            status_frame.pack(fill="x")
            ctk.CTkLabel(status_frame, text="Current Status: ", font=FONT_LABEL, text_color=G_TEXT).pack(side="left")
            ctk.CTkLabel(status_frame, text=issue['Status'], font=FONT_BODY, text_color=G_RED).pack(side="left")
            
            # Notes
            ctk.CTkLabel(cont, text="Observation Notes:", font=FONT_LABEL, text_color=G_TEXT).pack(anchor="w", pady=(10, 0))
            ctk.CTkLabel(cont, text=issue['Notes'], font=FONT_BODY, text_color=G_TEXT, 
                         wraplength=650, justify="left").pack(anchor="w", pady=(2, 0))

    def _add_field(self, parent, label_text, value_text, row_idx):
        """Helper to create a Label: Value row."""
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=1)
        ctk.CTkLabel(f, text=label_text, font=FONT_LABEL, text_color=G_SUBTEXT, width=110, anchor="w").pack(side="left")
        ctk.CTkLabel(f, text=value_text, font=FONT_BODY, text_color=G_TEXT, anchor="w").pack(side="left")