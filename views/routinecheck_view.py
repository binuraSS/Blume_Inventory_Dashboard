import customtkinter as ctk
from styles import *
from data.inventory import get_maintenance_list, mark_as_inspected

class RoutineCheckView(ctk.CTkFrame):
    def __init__(self, master, show_msg_cb=None):
        super().__init__(master, fg_color="transparent")
        self.show_msg = show_msg_cb
        
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Routine Maintenance", font=FONT_H1, text_color="black").pack(side="left")
        
        ctk.CTkButton(header, text="Refresh List", command=self.refresh, 
                      fg_color=G_BLUE, width=100).pack(side="right")

        # Scrollable Area
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="white", corner_radius=12, 
                                             border_width=1, border_color=G_BORDER)
        self.scroll.pack(fill="both", expand=True)
        
        self.refresh()

    def refresh(self):
        for w in self.scroll.winfo_children(): w.destroy()
        
        devices = get_maintenance_list()
        
        # Table Headers
        head_row = ctk.CTkFrame(self.scroll, fg_color="#F8F9FA", height=40)
        head_row.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(head_row, text="DEVICE ID", font=FONT_LABEL_BOLD, width=100).pack(side="left", padx=20)
        ctk.CTkLabel(head_row, text="CATEGORY", font=FONT_LABEL_BOLD, width=150).pack(side="left")
        ctk.CTkLabel(head_row, text="STATUS", font=FONT_LABEL_BOLD, width=120).pack(side="left")
        ctk.CTkLabel(head_row, text="COUNTDOWN", font=FONT_LABEL_BOLD, width=150).pack(side="left")

        for d in devices:
            row = ctk.CTkFrame(self.scroll, fg_color="transparent")
            row.pack(fill="x", pady=5)
            ctk.CTkFrame(self.scroll, height=1, fg_color=G_BORDER).pack(fill="x", padx=10) # Divider

            # ID & Category
            ctk.CTkLabel(row, text=d['bid'], font=("Arial", 12, "bold"), width=100).pack(side="left", padx=20)
            ctk.CTkLabel(row, text=d['category'], font=("Arial", 12), width=150, anchor="w").pack(side="left")
            
            # Status Badge
            badge = ctk.CTkFrame(row, fg_color=d['color'], corner_radius=12, width=100, height=24)
            badge.pack(side="left", padx=10)
            badge.pack_propagate(False)
            ctk.CTkLabel(badge, text=d['status'], text_color="white", font=("Arial", 10, "bold")).pack(expand=True)

            # Countdown Text
            days_text = f"{d['days_remaining']} days left" if d['days_remaining'] > 0 else f"{abs(d['days_remaining'])} days OVERDUE"
            ctk.CTkLabel(row, text=days_text, font=("Arial", 11), text_color=d['color'], width=150).pack(side="left")

            # Action Button
            if d['status'] != "Under Repair":
                ctk.CTkButton(row, text="Complete Inspection", font=("Arial", 11), 
                              fg_color="#F1F5F9", text_color="black", hover_color="#E2E8F0",
                              width=140, command=lambda b=d['bid']: self.handle_inspect(b)).pack(side="right", padx=20)

    def handle_inspect(self, bid):
        if mark_as_inspected(bid):
            if self.show_msg: self.show_msg(f"Device {bid} updated to Healthy!", "success")
            self.refresh()