import customtkinter as ctk
import database
import threading
from styles import *

class RepairView(ctk.CTkFrame):
    def __init__(self, master, show_msg_callback):
        super().__init__(master, fg_color=G_BG, corner_radius=12, border_width=1, border_color=G_BORDER)
        self.show_msg = show_msg_callback

        # Header Area
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(30, 10))
        ctk.CTkLabel(header, text="Repair Center", font=FONT_H1, text_color=G_TEXT).pack(side="left")

        # Scrollable List
        self.list_area = ctk.CTkScrollableFrame(self, fg_color=G_WINDOW_BG, corner_radius=8)
        self.list_area.pack(fill="both", expand=True, padx=30, pady=20)
        
        self.auto_refresh()

    def auto_refresh(self):
        if not self.winfo_exists():
            return
        
        # Check if the user is currently typing in any tech_entry box
        # This prevents the UI from wiping their notes every 30 seconds
        is_typing = False
        for card in self.list_area.winfo_children():
            for child in card.winfo_children(): # Check the card's children
                if isinstance(child, ctk.CTkFrame): # Check the input_side frame
                    for sub in child.winfo_children():
                        if isinstance(sub, ctk.CTkEntry) and len(sub.get()) > 0:
                            is_typing = True
                            break

        if not is_typing:
            self.load_tickets()
        
        self.after(30000, self.auto_refresh)

    def load_tickets(self):
        # We don't destroy here anymore; we destroy inside render 
        # to make the transition smoother if possible.
        def fetch():
            try:
                data = database.search_device("") 
                self.after(0, lambda d=data: self.render(d))
            except Exception as e:
                err = str(e)
                self.after(0, lambda msg=err: self.show_msg(f"Fetch Error: {msg}"))
                
        threading.Thread(target=fetch, daemon=True).start()

    def render(self, data):
        # Clear only when we have new data ready to show
        for w in self.list_area.winfo_children(): 
            w.destroy()
            
        for item in data:
            for issue in item.get('issues', []):
                self.create_repair_card(item, issue)

    def create_repair_card(self, item, issue):
        card = ctk.CTkFrame(self.list_area, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(fill="x", pady=8, padx=5)

        cont = ctk.CTkFrame(card, fg_color="transparent")
        cont.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        # Left Side: Info
        ctk.CTkLabel(cont, text=f"TICKET: {issue['Ticket ID']}", font=FONT_H2, text_color=G_RED).pack(anchor="w")
        ctk.CTkLabel(cont, text=f"Device: {item['Blume ID']} | Status: {issue['Status']}", font=FONT_BODY).pack(anchor="w")
        ctk.CTkLabel(cont, text=f"User Notes: {issue['Notes']}", font=FONT_LABEL, text_color=G_SUBTEXT).pack(anchor="w", pady=(5,0))

        # Right Side: Tech Input
        input_side = ctk.CTkFrame(card, fg_color="transparent")
        input_side.pack(side="right", padx=20, pady=10)

        tech_entry = ctk.CTkEntry(input_side, placeholder_text="Enter Tech Notes...", width=250)
        tech_entry.pack(pady=5)

        btn = ctk.CTkButton(input_side, text="Complete Repair", width=120, 
                            command=lambda t=issue['Ticket ID'], e=tech_entry: self.handle_resolve(t, e.get()))
        apply_material_button(btn, "primary")
        btn.pack(pady=5)

    def handle_resolve(self, tid, notes):
        if not notes.strip():
            self.show_msg("Please enter technician notes first!")
            return

        def task():
            try:
                if database.archive_resolved_ticket(tid, notes):
                    msg = f"Ticket {tid} archived to Sheet 4"
                    self.after(0, lambda m=msg: self.show_msg(m))
                    self.after(0, self.load_tickets)
                else:
                    self.after(0, lambda: self.show_msg("Error during archiving"))
            except Exception as e:
                err = str(e)
                self.after(0, lambda m=err: self.show_msg(f"System Error: {m}"))
        
        threading.Thread(target=task, daemon=True).start()