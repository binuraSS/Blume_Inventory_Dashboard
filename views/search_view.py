import customtkinter as ctk
import database
from styles import *

class SearchView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        p = ctk.CTkFrame(self, fg_color="transparent")
        p.pack(fill="both", expand=True, padx=20, pady=20)
        
        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))
        
        self.entry = ctk.CTkEntry(bar, placeholder_text="Search ID...", width=400, height=40)
        self.entry.pack(side="left", padx=10)
        
        btn = ctk.CTkButton(bar, text="Search", width=100, command=self.run_search)
        apply_material_button(btn, "primary")
        btn.pack(side="left")

        self.res_area = ctk.CTkScrollableFrame(p, fg_color=G_WINDOW_BG, corner_radius=8)
        self.res_area.pack(fill="both", expand=True)

    def run_search(self):
        for w in self.res_area.winfo_children(): w.destroy()
        results = database.search_device(self.entry.get())
        for item in results:
            issues = item.get('issues', [])
            if not issues:
                self.create_card(item, None)
            else:
                for issue in issues:
                    self.create_card(item, issue)

   # views/search_view.py

    def create_card(self, item, issue):
        card = ctk.CTkFrame(self.res_area, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(fill="x", pady=8, padx=15)
        
        accent_color = G_RED if issue else G_BLUE
        ctk.CTkFrame(card, width=6, fg_color=accent_color, corner_radius=0).pack(side="left", fill="y")
        
        cont = ctk.CTkFrame(card, fg_color="transparent")
        cont.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        # 1. Header (The Titles)
        h_f = ctk.CTkFrame(cont, fg_color="transparent")
        h_f.pack(fill="x", pady=(0, 10))
        
        if issue:
            self._add_header_text(h_f, "Ticket ID", issue['Ticket ID'])
            ctk.CTkLabel(h_f, text="  •  ", text_color=G_BORDER).pack(side="left")
            self._add_header_text(h_f, "Blume ID", item['Blume ID'])
        else:
            self._add_header_text(h_f, "Blume ID", item['Blume ID'])

        # --- 2. THE MISSING PART: Body Info ---
        body = ctk.CTkFrame(cont, fg_color="transparent")
        body.pack(fill="x")

        # Field: Category
        self._add_field(body, "Category", item['Item Category'])
        # Field: Serial Number
        self._add_field(body, "Serial No", item['Serial Number'])
        
        if issue:
            self._add_field(body, "Status", issue['Status'], is_error=True)
            # Add a separator for notes
            ctk.CTkFrame(cont, height=1, fg_color=G_BORDER).pack(fill="x", pady=10)
            ctk.CTkLabel(cont, text=issue['Notes'], font=FONT_BODY, text_color=G_TEXT, wraplength=600, justify="left").pack(anchor="w")
        else:
            self._add_field(body, "Status", "Operational")

    def _add_field(self, parent, label, value, is_error=False):
        """Standardized Material Row helper"""
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(fill="x", pady=2)
        ctk.CTkLabel(f, text=f"{label}: ", font=FONT_LABEL, text_color=G_SUBTEXT, width=100, anchor="w").pack(side="left")
        
        color = G_RED if is_error else G_TEXT
        ctk.CTkLabel(f, text=value, font=FONT_BODY, text_color=color).pack(side="left")

    def _add_header_text(self, parent, label, val):
        ctk.CTkLabel(parent, text=f"{label}: ", font=("Segoe UI", 18), text_color=G_SUBTEXT).pack(side="left")
        ctk.CTkLabel(parent, text=val, font=("Segoe UI", 18, "bold"), text_color=G_TEXT).pack(side="left")