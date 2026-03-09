import customtkinter as ctk
import threading
from styles import *
from data.inventory import search_device, get_maintenance_status, get_device_history, mark_as_inspected
from data.client import inventory_sheet, repair_sheet, safe_get_records

class SearchView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        
        # Main Padding Container
        p = ctk.CTkFrame(self, fg_color="transparent")
        p.pack(fill="both", expand=True, padx=20, pady=20)
        
        # --- Search Bar Area ---
        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))
        
        self.entry = ctk.CTkEntry(
            bar, 
            placeholder_text="Search Blume ID, Serial, or Status...", 
            width=400, 
            height=45,
            border_width=2,
            corner_radius=8
        )
        self.entry.pack(side="left", padx=10)
        self.entry.bind("<Return>", lambda e: self.run_search())
        
        self.search_btn = ctk.CTkButton(
            bar, 
            text="Search", 
            width=120, 
            height=45,
            command=self.run_search
        )
        apply_material_button(self.search_btn, "primary")
        self.search_btn.pack(side="left")

        # --- Results Scrollable Area ---
        self.res_area = ctk.CTkScrollableFrame(p, fg_color=G_WINDOW_BG, corner_radius=12)
        self.res_area.pack(fill="both", expand=True)

    def run_search(self):
        """Fetches data on a background thread to prevent UI freezing."""
        query = self.entry.get().strip()
        
        for w in self.res_area.winfo_children():
            w.destroy()
        
        self.search_btn.configure(state="disabled", text="Searching...")

        def task():
            try:
                # 1. Fetch reference data
                inv_data = safe_get_records(inventory_sheet)
                arc_data = safe_get_records(repair_sheet)
                
                # 2. Perform search
                results = search_device(query)
                
                # 3. Update UI
                self.after(0, lambda: self._render_results(results, inv_data, arc_data))
            except Exception as e:
                print(f"Search Engine Error: {e}")
                self.after(0, lambda: self.search_btn.configure(state="normal", text="Search"))

        threading.Thread(target=task, daemon=True).start()

    def _render_results(self, results, inv_data, arc_data):
        self.search_btn.configure(state="normal", text="Search")
        
        if not results:
            ctk.CTkLabel(self.res_area, text="No matching devices found.", font=FONT_BODY).pack(pady=40)
            return

        for item in results:
            self.create_device_result(item, inv_data, arc_data)

    def create_device_result(self, item, inv_data, arc_data):
        """Material Design Card with Detailed Timeline."""
        bid = item['Blume ID']
        last_date, days, is_overdue = get_maintenance_status(bid, inv_data, arc_data)
        
        card = ctk.CTkFrame(self.res_area, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(fill="x", pady=10, padx=15)
        
        # --- HEADER SECTION ---
        header_area = ctk.CTkFrame(card, fg_color="transparent")
        header_area.pack(fill="x", padx=20, pady=(20, 10))

        # Primary Topic: ID
        ctk.CTkLabel(header_area, text=bid, font=FONT_H2, text_color=G_BLUE).pack(side="left")

        # Sub-Topics: Meta Data
        meta_frame = ctk.CTkFrame(header_area, fg_color="transparent")
        meta_frame.pack(side="left", padx=30)
        
        ctk.CTkLabel(meta_frame, text=f"Category: {item.get('Item Category', 'N/A')}", 
                     font=FONT_LABEL, text_color=G_SUBTEXT).pack(anchor="w")
        ctk.CTkLabel(meta_frame, text=f"Serial: {item.get('Serial Number', 'N/A')}", 
                     font=FONT_LABEL, text_color=G_SUBTEXT).pack(anchor="w")

        if is_overdue:
            inspect_btn = ctk.CTkButton(header_area, text="Mark Inspected", width=130, height=35,
                                        command=lambda b=bid: self._handle_inspect(b))
            apply_material_button(inspect_btn, "primary")
            inspect_btn.pack(side="right")

        # --- ALERTS & FAULTS ---
        if is_overdue:
            banner = ctk.CTkFrame(card, fg_color="#FFF9E6", corner_radius=6)
            banner.pack(fill="x", padx=20, pady=(0, 15))
            ctk.CTkLabel(banner, text=f"⚠️ ATTENTION: {days} days since last inspection", 
                         font=FONT_LABEL_BOLD, text_color="#856404").pack(pady=6)

        if item.get('issues'):
            fault_container = ctk.CTkFrame(card, fg_color="transparent")
            fault_container.pack(fill="x", padx=20, pady=(0, 15))
            
            ctk.CTkLabel(fault_container, text="ACTIVE FAULTS", font=("Arial", 10, "bold"), text_color=G_RED).pack(anchor="w")
            
            for issue in item['issues']:
                row = ctk.CTkFrame(fault_container, fg_color="#FDF2F2", corner_radius=6)
                row.pack(fill="x", pady=2)
                ctk.CTkLabel(row, text=f"[{issue['Ticket ID']}]", font=FONT_BODY_BOLD, text_color=G_RED).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=f"{issue['Status']} — {issue['Notes']}", font=FONT_BODY, wraplength=550).pack(side="left", pady=8)

        # --- DETAILED TIMELINE ---
        ctk.CTkFrame(card, height=1, fg_color=G_BORDER).pack(fill="x", padx=20, pady=5)

        history_box = ctk.CTkFrame(card, fg_color="transparent")
        history_box.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkLabel(history_box, text="DEVICE TIMELINE", font=("Arial", 10, "bold"), text_color=G_SUBTEXT).pack(anchor="w", pady=(0, 10))

        history = get_device_history(bid)
        for entry in history[:5]:
            h_row = ctk.CTkFrame(history_box, fg_color="transparent")
            h_row.pack(fill="x", pady=4)
            
            # Header line for the event
            top_line = ctk.CTkFrame(h_row, fg_color="transparent")
            top_line.pack(fill="x")
            
            ctk.CTkLabel(top_line, text=entry['date'], font=("Arial", 11, "bold"), text_color=G_SUBTEXT, width=90).pack(side="left")
            ctk.CTkLabel(top_line, text=f"• {entry['event']}", font=("Arial", 12, "bold"), text_color=entry.get('color', G_TEXT)).pack(side="left", padx=5)
            
            # Detail line (The "Point" of the entry)
            if entry.get('details'):
                detail_lbl = ctk.CTkLabel(
                    h_row, 
                    text=f"      {entry['details']}", 
                    font=FONT_LABEL, 
                    text_color=G_TEXT, 
                    wraplength=600, 
                    justify="left"
                )
                detail_lbl.pack(anchor="w", padx=10)

    def _handle_inspect(self, bid):
        def task():
            try:
                if mark_as_inspected(bid):
                    self.after(0, self.run_search)
            except Exception as e:
                print(f"Inspection Update Error: {e}")
        
        threading.Thread(target=task, daemon=True).start()