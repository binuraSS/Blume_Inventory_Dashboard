import customtkinter as ctk
from styles import *
import database

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, show_msg_cb=None):
        super().__init__(master, fg_color="transparent")
        self.show_msg = show_msg_cb
        self.sync_label = ctk.CTkLabel(self, text="Syncing...", font=FONT_LABEL, text_color=G_SUBTEXT)
        self.sync_label.pack(side="bottom", anchor="e", padx=20, pady=10)
        
        # --- TOP LAYER: HEADER & SCORE ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Fleet Overview", font=FONT_H1).pack(side="left")
        self.score_label = ctk.CTkLabel(header, text="Health: --%", font=FONT_H2, text_color=G_BLUE)
        self.score_label.pack(side="right")

        # --- MIDDLE LAYER: PULSE CARDS ---
        self.card_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.card_frame.pack(fill="x")
        self.cards = {}
        self._create_card("Active Faults", G_RED, "broken")
        self._create_card("Maintenance Due", G_YELLOW, "overdue")
        self._create_card("Healthy Fleet", G_GREEN, "healthy")

        # --- BOTTOM LAYER: TWO COLUMNS (Insights & Live Feed) ---
        bottom_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_row.pack(fill="both", expand=True, pady=20)
        bottom_row.grid_columnconfigure(0, weight=2) 
        bottom_row.grid_columnconfigure(1, weight=1) 

        # Column 1: Main Content (System Insights)
        self.main_content = ctk.CTkFrame(bottom_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.main_content.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(self.main_content, text="System Insights", font=FONT_LABEL_BOLD).pack(pady=10)
        
        self.refresh_btn = ctk.CTkButton(self.main_content, text="Manual Sync", command=self.refresh_data)
        apply_material_button(self.refresh_btn, "secondary")
        self.refresh_btn.pack(side="bottom", pady=20)

        # Column 2: Live Activity Feed
        self.feed_box = ctk.CTkFrame(bottom_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.feed_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(self.feed_box, text="Recent Activity", font=FONT_LABEL_BOLD).pack(pady=10)
        
        self.feed_container = ctk.CTkScrollableFrame(self.feed_box, fg_color="transparent", height=300)
        self.feed_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Start the background Pulse (Every 30 seconds)
        self.start_auto_refresh()

    def _create_card(self, title, color, key):
        card = ctk.CTkFrame(self.card_frame, fg_color="white", corner_radius=12, border_width=2, border_color=color)
        card.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(card, text=title, font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0))
        val = ctk.CTkLabel(card, text="--", font=FONT_PULSE, text_color=color)
        val.pack(pady=20)
        self.cards[key] = val

    def start_auto_refresh(self):
        self.refresh_data()
        self.after(30000, self.start_auto_refresh)

    def update_feed(self, events):
        """Clears and repopulates the Recent Activity list."""
        for w in self.feed_container.winfo_children():
            w.destroy()
        
        if not events:
            ctk.CTkLabel(self.feed_container, text="No recent activity", font=FONT_BODY, text_color=G_SUBTEXT).pack(pady=10)
            return

        for e in events:
            line = ctk.CTkFrame(self.feed_container, fg_color="#F8F9FA", corner_radius=6)
            line.pack(fill="x", pady=2)
            ctk.CTkLabel(line, text="●", text_color=e['color'], font=("Arial", 12)).pack(side="left", padx=5)
            ctk.CTkLabel(line, text=f"{e['bid']}: {e['event']}", font=FONT_BODY, text_color=G_TEXT).pack(side="left")

    def refresh_data(self):
        """Live sync with database.py"""
        try:
            # 1. Update Cards
            stats = database.get_fleet_stats()
            self.cards["broken"].configure(text=str(stats["broken"]))
            self.cards["overdue"].configure(text=str(stats["overdue"]))
            self.cards["healthy"].configure(text=str(stats["healthy"]))

            # 2. Update Health Score
            total = sum(stats.values())
            score = int((stats["healthy"] / total) * 100) if total > 0 else 0
            self.score_label.configure(text=f"Health: {score}%")

           # 3. Update Insights (With Visual Bars)
            insights = database.get_system_insights()
            for w in self.main_content.winfo_children():
                if isinstance(w, ctk.CTkFrame): w.destroy()
            
            # Calculate total issues to determine bar widths
            total_issues = sum(count for cat, count in insights)

            for cat, count in insights[:5]:
                # Row Container
                row = ctk.CTkFrame(self.main_content, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=8)
                
                # Labels
                ctk.CTkLabel(row, text=cat, font=FONT_BODY).pack(side="left")
                ctk.CTkLabel(row, text=str(count), font=FONT_BODY_BOLD, text_color=G_RED).pack(side="right")
                
                # --- THE VISUAL BAR ---
                # Calculate width percentage (max width 300px)
                width_pct = (count / total_issues) if total_issues > 0 else 0
                bar_bg = ctk.CTkFrame(self.main_content, height=6, fg_color="#E0E0E0", corner_radius=3)
                bar_bg.pack(fill="x", padx=20, pady=(0, 10))
                
                # The "Fill" of the bar
                fill_width = int(width_pct * 1) # Relative to parent
                bar_fill = ctk.CTkFrame(bar_bg, width=0, height=6, fg_color=G_BLUE, corner_radius=3)
                bar_fill.place(relwidth=width_pct, relheight=1)

            # 4. Update Recent Activity Feed
            self.update_feed(database.get_recent_activity())

            # --- UPDATE TIMESTAMP ---
            from datetime import datetime
            now = datetime.now().strftime("%H:%M:%S")
            self.sync_label.configure(text=f"Last Synced: {now}")

        except Exception as e:
            print(f"UI Refresh Error: {e}")
            self.sync_label.configure(text="Sync Failed", text_color=G_RED)