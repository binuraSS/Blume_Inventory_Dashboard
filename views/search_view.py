import customtkinter as ctk
import database
from styles import *

class SearchView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        p = ctk.CTkFrame(self, fg_color="transparent")
        p.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Search Bar
        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))
        
        self.entry = ctk.CTkEntry(bar, placeholder_text="Search Blume ID or Status...", width=400, height=40)
        self.entry.pack(side="left", padx=10)
        self.entry.bind("<Return>", lambda e: self.run_search())
        
        btn = ctk.CTkButton(bar, text="Search", width=100, command=self.run_search)
        apply_material_button(btn, "primary")
        btn.pack(side="left")

        # Results Area
        self.res_area = ctk.CTkScrollableFrame(p, fg_color=G_WINDOW_BG, corner_radius=8)
        self.res_area.pack(fill="both", expand=True)

    def run_search(self):
        for w in self.res_area.winfo_children(): w.destroy()
        query = self.entry.get().strip()
        if not query: return
        
        results = database.search_device(query)
        for item in results:
            self.create_device_result(item)

    def create_device_result(self, item):
        bid = item['Blume ID']
        
        # 1. Check Maintenance Status (Pulse Logic)
        status_text, status_color = database.get_maintenance_status(bid)
        is_overdue = "Overdue" in status_text

        card = ctk.CTkFrame(self.res_area, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(fill="x", pady=10, padx=15)
        
        # --- MAINTENANCE BANNER (Only shows if Overdue) ---
        if is_overdue:
            banner = ctk.CTkFrame(card, fg_color=status_color, height=35, corner_radius=12)
            banner.pack(fill="x", padx=10, pady=(10, 0))
            ctk.CTkLabel(banner, text=f"⚠️ {status_text}", text_color="black", font=FONT_LABEL_BOLD).pack(pady=5)

        # Header Section
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        self._add_header_text(header, "Blume ID", bid)
        ctk.CTkLabel(header, text=f"  ({item['Item Category']})", font=FONT_BODY, text_color=G_SUBTEXT).pack(side="left")
        
        # Quick Action Button (Mark as Inspected)
        if is_overdue:
            ins_btn = ctk.CTkButton(header, text="Mark as Inspected", width=140, height=30,
                                     command=lambda b=bid: self.handle_quick_inspect(b))
            apply_material_button(ins_btn, "secondary")
            ins_btn.pack(side="right", padx=10)

        # Device Info Row
        info_row = ctk.CTkFrame(card, fg_color="transparent")
        info_row.pack(fill="x", padx=20, pady=(0, 10))
        
        # Show Last Service Date in the info row
        last_s = item.get('Last Service', 'Never')
        ctk.CTkLabel(info_row, text=f"Serial: {item['Serial Number']}  |  Last Service: {last_s}", 
                     font=FONT_LABEL, text_color=G_SUBTEXT).pack(side="left")

        # --- THE TIMELINE SECTION ---
        ctk.CTkLabel(card, text="Device History & Status Timeline", font=FONT_LABEL_BOLD, text_color=G_BLUE).pack(anchor="w", padx=20, pady=(10, 5))
        
        timeline_box = ctk.CTkFrame(card, fg_color="#F8F9FA", corner_radius=8, border_width=1, border_color="#E0E0E0")
        timeline_box.pack(fill="x", padx=20, pady=(0, 20))

        history = database.get_device_history(bid)
        if not history:
            ctk.CTkLabel(timeline_box, text="No repair history found.", font=FONT_LABEL).pack(pady=10)
        else:
            for entry in history:
                self._add_timeline_node(timeline_box, entry)

    def handle_quick_inspect(self, bid):
        """Resets the clock and refreshes the search view."""
        if database.mark_as_inspected(bid):
            self.run_search() # Live Refresh!

    def _add_timeline_node(self, parent, entry):
        node = ctk.CTkFrame(parent, fg_color="transparent")
        node.pack(fill="x", padx=15, pady=5)
        
        indicator = ctk.CTkLabel(node, text="●", font=("Arial", 18), text_color=entry['color'])
        indicator.pack(side="left", anchor="n", pady=2)
        
        details = ctk.CTkFrame(node, fg_color="transparent")
        details.pack(side="left", fill="x", expand=True, padx=10)
        
        top_line = f"{entry['date']} — {entry['event']}"
        ctk.CTkLabel(details, text=top_line, font=FONT_BODY_BOLD, text_color=G_TEXT).pack(anchor="w")
        
        if entry.get('notes'):
            ctk.CTkLabel(details, text=entry['notes'], font=FONT_LABEL, text_color=G_SUBTEXT, wraplength=500, justify="left").pack(anchor="w")

    def _add_header_text(self, parent, label, val):
        ctk.CTkLabel(parent, text=f"{label}: ", font=("Segoe UI", 18), text_color=G_SUBTEXT).pack(side="left")
        ctk.CTkLabel(parent, text=val, font=("Segoe UI", 18, "bold"), text_color=G_TEXT).pack(side="left")