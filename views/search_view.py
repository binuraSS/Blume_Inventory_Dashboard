import customtkinter as ctk
import threading
from styles import *
from data.inventory import search_device, get_maintenance_status, get_device_history, mark_as_inspected
from data.client import inventory_sheet, repair_sheet, safe_get_records

class SearchView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # --- Search Bar ---
        search_bar = ctk.CTkFrame(container, fg_color="transparent")
        search_bar.pack(fill="x", pady=(0, 20))

        self.entry = ctk.CTkEntry(search_bar, placeholder_text="Search Blume ID...", width=420, height=42)
        self.entry.pack(side="left", padx=(0, 10))
        self.entry.bind("<Return>", lambda e: self.run_search())

        self.search_btn = ctk.CTkButton(search_bar, text="Search", width=120, height=42, command=self.run_search)
        apply_material_button(self.search_btn, "primary")
        self.search_btn.pack(side="left")

        self.res_area = ctk.CTkScrollableFrame(container, fg_color=G_WINDOW_BG, corner_radius=10)
        self.res_area.pack(fill="both", expand=True)

    def run_search(self):
        query = self.entry.get().strip()
        for widget in self.res_area.winfo_children(): widget.destroy()
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
            ctk.CTkLabel(self.res_area, text="No matching devices found.", font=("Arial", 14)).pack(pady=40)
            return
        for item in results:
            self.create_device_card(item, inv_data, arc_data)

    def create_device_card(self, item, inv_data, arc_data):
        bid = item["Blume ID"]
        last_date, days, is_overdue = get_maintenance_status(bid, inv_data, arc_data)
        
        # Main Card: Remove height, let it expand vertically based on content
        card = ctk.CTkFrame(self.res_area, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(fill="x", padx=10, pady=10)

        # --- Main Header ---
        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(header, text=bid, font=("Arial", 16, "bold"), text_color="#111111").pack(side="left")
        
        meta = f"  •  {item.get('Item Category')}  •  SN: {item.get('Serial Number')}"
        ctk.CTkLabel(header, text=meta, font=("Arial", 11, "bold"), text_color=G_SUBTEXT).pack(side="left")

        if is_overdue:
            inspect_btn = ctk.CTkButton(header, text="Inspect", width=80, height=28, command=lambda: self._handle_inspect(bid))
            apply_material_button(inspect_btn, "primary")
            inspect_btn.pack(side="right")
            
            # This label adds vertical height only when overdue
            ctk.CTkLabel(card, text=f"⚠️ Overdue ({days} days)", text_color="#856404", font=("Arial", 11, "bold")).pack(anchor="w", padx=20, pady=(0, 5))

        # Separator line
        ctk.CTkFrame(card, height=1, fg_color="#F2F2F2").pack(fill="x", padx=20, pady=5)

        # --- Timeline Section ---
        history_container = ctk.CTkFrame(card, fg_color="transparent")
        history_container.pack(fill="x", padx=20, pady=(10, 20))

        # Vertical Track Line
       # timeline_line = ctk.CTkFrame(history_container, width=2, fg_color="#E0E0E0")
        #timeline_line.place(x=20, rely=0, relheight=1) 

        history = get_device_history(bid)
        for entry in history[:5]:
            # Event Wrapper: No fixed height here
            ev_wrapper = ctk.CTkFrame(history_container, fg_color="transparent")
            ev_wrapper.pack(fill="x", pady=4)

            # Gutter to align with the line
            ctk.CTkFrame(ev_wrapper, width=40, height=1, fg_color="transparent").pack(side="left")

            # Small Card: Now fits internal content exactly
            small_card = ctk.CTkFrame(ev_wrapper, fg_color="#F8F9FA", corner_radius=8, border_width=1, border_color="#E8E8E8")
            small_card.pack(side="left", fill="x", expand=True, padx=(5, 10))

            # Title & Date Row
            title_row = ctk.CTkFrame(small_card, fg_color="transparent")
            title_row.pack(fill="x", padx=12, pady=(8, 4))
            
            # Logic for Node Color
            ev_text = str(entry["event"]).upper()
            node_color = G_BLUE
            if "FAULT" in ev_text: node_color = G_RED
            elif "REPAIR" in ev_text: node_color = "#166534"

            # Status Dot
            ctk.CTkFrame(title_row, width=8, height=8, corner_radius=4, fg_color=node_color).pack(side="left", padx=(0, 8))
            
            ctk.CTkLabel(title_row, text=ev_text, font=("Arial", 11, "bold"), text_color=node_color).pack(side="left")
            ctk.CTkLabel(title_row, text=entry["date"], font=("Arial", 10), text_color=G_SUBTEXT).pack(side="right")

            # Details: Use wraplength to ensure it grows vertically, not horizontally
            if entry.get("details"):
                # Padding left (28) aligns text under the Title, skipping the dot area
                details_label = ctk.CTkLabel(small_card, text=entry["details"], font=("Arial", 10), 
                                           text_color="#444444", wraplength=400, justify="left")
                details_label.pack(anchor="w", padx=(28, 12), pady=(0, 8))
                
    def _handle_inspect(self, bid):
        def task():
            if mark_as_inspected(bid): self.after(0, self.run_search)
        threading.Thread(target=task, daemon=True).start()