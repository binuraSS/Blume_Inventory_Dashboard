# views/dashboard_view.py
import customtkinter as ctk
from styles import *
import database

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, show_msg_cb=None):
        # Using G_WINDOW_BG to contrast against the white sidebar
        super().__init__(master, fg_color="transparent")
        self.show_msg = show_msg_cb

        # --- HEADER SECTION ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 30))

        ctk.CTkLabel(header_frame, text="Fleet Overview", font=FONT_H1, text_color=G_TEXT).pack(side="left")
        
        # System Health Percentage Label
        self.health_score_label = ctk.CTkLabel(header_frame, text="Score: --%", font=FONT_H2, text_color=G_BLUE)
        self.health_score_label.pack(side="right", padx=20)

        # --- PULSE CONTAINER (The Big Numbers) ---
        self.pulse_container = ctk.CTkFrame(self, fg_color="transparent")
        self.pulse_container.pack(fill="x", pady=10)

        # Create the three Pulse Cards
        self.cards = {}
        self._create_pulse_card("Active Faults", G_RED, "broken")
        self._create_pulse_card("Maintenance Due", G_YELLOW, "overdue")
        self._create_pulse_card("Healthy Fleet", G_GREEN, "healthy")

        # --- ACTION AREA ---
        info_box = ctk.CTkFrame(self, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        info_box.pack(fill="both", expand=True, pady=20)
        
        ctk.CTkLabel(info_box, text="Quick Actions & Insights", font=FONT_LABEL_BOLD, text_color=G_TEXT).pack(pady=15)
        
        # Functional Buttons
        btn_row = ctk.CTkFrame(info_box, fg_color="transparent")
        btn_row.pack(pady=10)

        self.refresh_btn = ctk.CTkButton(btn_row, text="🔄 Refresh Stats", command=self.refresh_data)
        apply_material_button(self.refresh_btn, "primary")
        self.refresh_btn.pack(side="left", padx=10)

        # Automatically refresh when the view is opened
        self.after(500, self.refresh_data)

    def _create_pulse_card(self, title, color, key):
        """Helper to create the 🟢🟡🔴 metric cards."""
        card = ctk.CTkFrame(self.pulse_container, fg_color="white", corner_radius=12, 
                            border_width=2, border_color=color, width=220, height=180)
        card.pack(side="left", padx=10, expand=True)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text=title, font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(20, 0))
        
        # Big Pulse Number
        val_label = ctk.CTkLabel(card, text="--", font=FONT_PULSE, text_color=color)
        val_label.pack(expand=True)
        self.cards[key] = val_label

    def refresh_data(self):
        """Fetches live data from database.py and updates UI."""
        # 1. Loading State
        for key in self.cards:
            self.cards[key].configure(text="..." )
        
        # 2. Call the Database
        try:
            stats = database.get_fleet_stats()
            
            # 3. Update Cards
            self.cards["broken"].configure(text=str(stats["broken"]))
            self.cards["overdue"].configure(text=str(stats["overdue"]))
            self.cards["healthy"].configure(text=str(stats["healthy"]))

            # 4. Calculate Health Score %
            total = stats["broken"] + stats["overdue"] + stats["healthy"]
            if total > 0:
                # Formula: Healthy / Total Fleet
                score = int((stats["healthy"] / total) * 100)
                self.health_score_label.configure(text=f"System Health: {score}%")
                
                # Dynamic color for the score
                if score > 90: self.health_score_label.configure(text_color=G_GREEN)
                elif score > 70: self.health_score_label.configure(text_color=G_YELLOW)
                else: self.health_score_label.configure(text_color=G_RED)

            if self.show_msg:
                self.show_msg("System Pulse Updated")

        except Exception as e:
            if self.show_msg:
                self.show_msg(f"Update Failed: {str(e)}")