import customtkinter as ctk
import database
import threading
from styles import *

class RepairView(ctk.CTkFrame):
    def __init__(self, master, show_msg_callback):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        self.show_msg = show_msg_callback

        # --- Header ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header, text="Repair Workshop", font=FONT_H1, text_color=G_TEXT).pack(side="left")
        
        refresh_btn = ctk.CTkButton(header, text="🔄 Refresh Board", width=120, command=self.load_tickets)
        apply_material_button(refresh_btn, "primary")
        refresh_btn.pack(side="right")

        # --- Kanban Board (2 Columns) ---
        self.board = ctk.CTkFrame(self, fg_color="transparent")
        self.board.pack(fill="both", expand=True, padx=20, pady=10)

        # Left Column: New Arrivals
        self.col_intake = self._create_column("📥 INTAKE / NEW FAULTS", G_BLUE)
        # Right Column: Active Work
        self.col_progress = self._create_column("🛠️ IN PROGRESS", G_ORANGE)

        self.load_tickets()

    def _create_column(self, title, color):
        col_container = ctk.CTkFrame(self.board, fg_color="#F1F2F6", corner_radius=10)
        col_container.pack(side="left", fill="both", expand=True, padx=10)
        
        head = ctk.CTkFrame(col_container, fg_color=color, height=40, corner_radius=10)
        head.pack(fill="x", padx=5, pady=5)
        ctk.CTkLabel(head, text=title, font=FONT_BODY_BOLD, text_color="white").pack(pady=5)
        
        scroll = ctk.CTkScrollableFrame(col_container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=2, pady=2)
        return scroll

    def load_tickets(self):
        def fetch():
            try:
                # Searching with empty string returns all devices with active issues
                data = database.search_device("") 
                self.after(0, lambda d=data: self.render(d))
            except Exception as e:
                self.after(0, lambda: self.show_msg(f"Fetch Error: {str(e)}"))
                
        threading.Thread(target=fetch, daemon=True).start()

    def render(self, data):
        # QUOTA PROTECTION: Fetch reference data once per render
        try:
            inv_data = database.inventory_sheet.get_all_records()
            arc_data = database.repair_sheet.get_all_records()
        except Exception as e:
            print(f"Quota Error during render: {e}")
            return

        for col in [self.col_intake, self.col_progress]:
            for w in col.winfo_children(): w.destroy()
            
        for item in data:
            for issue in item.get('issues', []):
                # Maintenance Check
                _, days, is_stale = database.get_maintenance_status(item['Blume ID'], inv_data, arc_data)
                
                # LOOKUP: Use your new header name "Progress Level"
                raw_status = issue.get('Progress Level', 'PENDING')
                status = str(raw_status).upper().strip()
                
                # ROUTING
                if "PROGRESS" in status:
                    self.create_progress_card(self.col_progress, item, issue)
                else:
                    self.create_intake_card(self.col_intake, item, issue, is_stale, days)

    def create_intake_card(self, parent, item, issue, is_stale, days):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=1, border_color="#E0E0E0")
        card.pack(fill="x", pady=6, padx=5)

        # Maintenance Alert Banner
        if is_stale:
            banner = ctk.CTkFrame(card, fg_color="#FFF3CD", height=26, corner_radius=4)
            banner.pack(fill="x", padx=8, pady=8)
            ctk.CTkLabel(banner, text=f"⚠️ FLAG: UNCHECKED FOR {days} DAYS", 
                         font=("Segoe UI", 10, "bold"), text_color="#856404").pack(pady=2)

        ctk.CTkLabel(card, text=f"ID: {item['Blume ID']}", font=FONT_BODY_BOLD, text_color=G_BLUE).pack(anchor="w", padx=12, pady=(5,0))
        ctk.CTkLabel(card, text=f"Issue: {issue['Notes']}", font=FONT_LABEL, text_color=G_SUBTEXT, wraplength=220, justify="left").pack(anchor="w", padx=12, pady=5)

        btn = ctk.CTkButton(card, text="Start Repair →", height=32, 
                            command=lambda t=issue['Ticket ID']: self.update_status(t, "In Progress"))
        apply_material_button(btn, "primary")
        btn.pack(fill="x", padx=10, pady=10)

    def create_progress_card(self, parent, item, issue):
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=8, border_width=2, border_color=G_ORANGE)
        card.pack(fill="x", pady=6, padx=5)

        ctk.CTkLabel(card, text=f"REPAIRING: {item['Blume ID']}", font=FONT_BODY_BOLD).pack(anchor="w", padx=12, pady=(10,0))
        
        # Tech Entry Box
        entry = ctk.CTkEntry(card, placeholder_text="Describe the fix...", height=30, font=FONT_LABEL)
        entry.pack(fill="x", padx=10, pady=10)

        # Quick Action Chips
        tags_f = ctk.CTkFrame(card, fg_color="transparent")
        tags_f.pack(fill="x", padx=10, pady=(0, 10))
        for tag in ["Cleaned", "Reset", "Fixed", "Screen"]:
            t_btn = ctk.CTkButton(tags_f, text=tag, width=45, height=22, font=("Arial", 9), fg_color="#F1F2F6", text_color=G_TEXT)
            t_btn.configure(command=lambda e=entry, t=tag: self._quick_add(e, t))
            t_btn.pack(side="left", padx=2)

        # Complete/Archive Button
        comp_btn = ctk.CTkButton(card, text="✅ Complete & Archive", fg_color="#27AE60", hover_color="#219150",
                                 command=lambda t=issue['Ticket ID'], e=entry: self.handle_resolve(t, e.get()))
        comp_btn.pack(fill="x", padx=10, pady=(0, 10))

    def _quick_add(self, entry, text):
        curr = entry.get()
        entry.delete(0, "end")
        entry.insert(0, f"{curr} {text},".strip())

    def update_status(self, tid, new_status):
        """Moves a card from Intake to Progress by updating the sheet"""
        def task():
            if database.update_ticket_status(tid, new_status):
                # Wait 1 second before refreshing so Google can update the data
                self.after(1000, self.load_tickets)
            else:
                self.after(0, lambda: self.show_msg("Failed to start repair."))
        
        threading.Thread(target=task, daemon=True).start()

    def handle_resolve(self, tid, notes):
        if not notes.strip():
            self.show_msg("Please enter technician notes first!")
            return

        def task():
            try:
                if database.archive_resolved_ticket(tid, notes):
                    self.after(0, lambda: self.show_msg(f"Ticket {tid} resolved!"))
                    # Wait 1 second before refreshing
                    self.after(1000, self.load_tickets)
                else:
                    self.after(0, lambda: self.show_msg("Error archiving ticket."))
            except Exception as e:
                self.after(0, lambda: self.show_msg(f"System Error: {str(e)}"))
        
        threading.Thread(target=task, daemon=True).start()
