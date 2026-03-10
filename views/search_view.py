import customtkinter as ctk
import threading
from styles import *
from data.inventory import search_device, get_maintenance_status, get_device_history, mark_as_inspected
from data.client import inventory_sheet, repair_sheet, safe_get_records

class SearchView(ctk.CTkFrame):
    def __init__(self, master):
        # Use G_WINDOW_BG for the main background container
        super().__init__(master, fg_color=G_WINDOW_BG, corner_radius=0)

        # --- 1. Page Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(20, 10), padx=30)
        
        ctk.CTkLabel(
            header, 
            text="Search Inventory", 
            font=FONT_H1, 
            text_color=G_TEXT
        ).pack(side="left")

        # --- 2. Search Bar Area ---
        # A container card for the search tools
        search_card = ctk.CTkFrame(self, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        search_card.pack(fill="x", padx=30, pady=10)
        
        search_inner = ctk.CTkFrame(search_card, fg_color="transparent")
        search_inner.pack(padx=20, pady=20)

        self.entry = ctk.CTkEntry(
            search_inner, 
            placeholder_text="Enter Blume ID (e.g. BL-001)...", 
            width=420, 
            height=42,
            fg_color=G_WINDOW_BG, # Slightly different shade for input
            border_color=G_BORDER,
            text_color=G_TEXT
        )
        self.entry.pack(side="left", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.run_search())

        self.search_btn = ctk.CTkButton(search_inner, text="Search", width=120, height=42, command=self.run_search)
        apply_material_button(self.search_btn, "primary")
        self.search_btn.pack(side="left")

        # --- 3. Results Scroll Area ---
        self.res_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.res_area.pack(fill="both", expand=True, padx=20, pady=10)

    def run_search(self):
        query = self.entry.get().strip()
        if not query: return
        
        # Clear previous results
        for widget in self.res_area.winfo_children(): 
            widget.destroy()
            
        self.search_btn.configure(state="disabled", text="Searching...")

        def task():
            try:
                inv_data = safe_get_records(inventory_sheet)
                arc_data = safe_get_records(repair_sheet)
                results = search_device(query)
                self.after(0, lambda: self._render_results(results, inv_data, arc_data))
            except Exception as e:
                print(f"Search error: {e}")
                self.after(0, lambda: self.search_btn.configure(state="normal", text="Search"))

        threading.Thread(target=task, daemon=True).start()

    def _render_results(self, results, inv_data, arc_data):
        self.search_btn.configure(state="normal", text="Search")
        if not results:
            ctk.CTkLabel(self.res_area, text="No matching devices found.", font=FONT_BODY, text_color=G_SUBTEXT).pack(pady=40)
            return
            
        for item in results:
            self.create_device_card(item, inv_data, arc_data)

    def create_device_card(self, item, inv_data, arc_data):
        bid = item["Blume ID"]
        last_date, days, is_overdue = get_maintenance_status(bid, inv_data, arc_data)
        
        # Main Device Card
        card = ctk.CTkFrame(self.res_area, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(fill="x", padx=10, pady=10)

        # --- Card Header ---
        card_header = ctk.CTkFrame(card, fg_color="transparent")
        card_header.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(card_header, text=bid, font=FONT_H2, text_color=G_TEXT).pack(side="left")
        
        meta = f"  •  {item.get('Item Category')}  •  SN: {item.get('Serial Number')}"
        ctk.CTkLabel(card_header, text=meta, font=FONT_BODY, text_color=G_SUBTEXT).pack(side="left")

        if is_overdue:
            inspect_btn = ctk.CTkButton(card_header, text="Inspect", width=80, height=28, command=lambda: self._handle_inspect(bid))
            apply_material_button(inspect_btn, "primary")
            inspect_btn.pack(side="right")
            
            ctk.CTkLabel(card, text=f"⚠️ Maintenance Overdue ({days} days)", 
                         text_color=G_RED, font=FONT_LABEL).pack(anchor="w", padx=20, pady=(0, 5))

        # Separator Line
        ctk.CTkFrame(card, height=1, fg_color=G_BORDER).pack(fill="x", padx=20, pady=5)

        # --- Timeline/History Section ---
        history_container = ctk.CTkFrame(card, fg_color="transparent")
        history_container.pack(fill="x", padx=20, pady=(10, 20))

        history = get_device_history(bid)
        if not history:
            ctk.CTkLabel(history_container, text="No history recorded for this device.", 
                         font=FONT_BODY, text_color=G_SUBTEXT).pack(anchor="w", pady=5)
        
        for entry in history[:5]:
            ev_wrapper = ctk.CTkFrame(history_container, fg_color="transparent")
            ev_wrapper.pack(fill="x", pady=4)

            ctk.CTkFrame(ev_wrapper, width=20, height=1, fg_color="transparent").pack(side="left")

            small_card = ctk.CTkFrame(ev_wrapper, fg_color=G_WINDOW_BG, corner_radius=8, border_width=1, border_color=G_BORDER)
            small_card.pack(side="left", fill="x", expand=True, padx=(5, 10))

            title_row = ctk.CTkFrame(small_card, fg_color="transparent")
            title_row.pack(fill="x", padx=12, pady=(8, 4))
            
            ev_text = str(entry["event"]).upper()
            node_color = G_BLUE
            if "FAULT" in ev_text: node_color = G_RED
            elif "REPAIR" in ev_text: node_color = G_GREEN

            ctk.CTkFrame(title_row, width=8, height=8, corner_radius=4, fg_color=node_color).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(title_row, text=ev_text, font=FONT_LABEL, text_color=node_color).pack(side="left")
            ctk.CTkLabel(title_row, text=entry["date"], font=FONT_BODY, text_color=G_SUBTEXT).pack(side="right")

            # --- KEY FIX HERE ---
            # We look for 'Device Status' or 'details' (if your helper function renames it)
            # We also strip it and check if it's not 'None'
            raw_details = entry.get("Device Status") or entry.get("details") or ""
            details_text = str(raw_details).strip()

            if details_text and details_text.lower() != "none":
                details_label = ctk.CTkLabel(
                    small_card, 
                    text=details_text, 
                    font=FONT_BODY, 
                    text_color=G_TEXT, 
                    wraplength=500, 
                    justify="left"
                )
                details_label.pack(anchor="w", padx=(28, 12), pady=(0, 8))
                
    def _handle_inspect(self, bid):
        def task():
            if mark_as_inspected(bid): 
                self.after(0, self.run_search)
        threading.Thread(target=task, daemon=True).start()