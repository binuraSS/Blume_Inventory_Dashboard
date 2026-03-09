import customtkinter as ctk
from styles import *
from data.stats import get_fleet_stats, get_system_insights, get_recent_activity

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, show_msg_cb=None):
        super().__init__(master, fg_color="transparent")
        self.show_msg = show_msg_cb
        
        # --- Header & Score ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Fleet Overview", font=FONT_H1).pack(side="left")
        self.score_label = ctk.CTkLabel(header, text="Health: --%", font=FONT_H2, text_color=G_BLUE)
        self.score_label.pack(side="right")

        # --- Pulse Cards ---
        self.card_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.card_frame.pack(fill="x")
        self.cards = {}
        self._create_card("Active Faults", G_RED, "broken")
        self._create_card("Maintenance Due", G_YELLOW, "overdue")
        self._create_card("Healthy Fleet", G_GREEN, "healthy")

        # --- Insights & Feed Columns ---
        bottom_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_row.pack(fill="both", expand=True, pady=20)
        bottom_row.grid_columnconfigure(0, weight=2) 
        bottom_row.grid_columnconfigure(1, weight=1) 

        # Left: Visual Insights
        self.main_content = ctk.CTkFrame(bottom_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.main_content.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(self.main_content, text="System Insights", font=FONT_LABEL_BOLD).pack(pady=10)

        # Right: Activity Feed
        self.feed_box = ctk.CTkFrame(bottom_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.feed_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(self.feed_box, text="Recent Activity", font=FONT_LABEL_BOLD).pack(pady=10)
        self.feed_container = ctk.CTkScrollableFrame(self.feed_box, fg_color="transparent", height=300)
        self.feed_container.pack(fill="both", expand=True, padx=5, pady=5)

        self.refresh_data()

    def _create_card(self, title, color, key):
        card = ctk.CTkFrame(self.card_frame, fg_color="white", corner_radius=12, border_width=2, border_color=color)
        card.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(card, text=title, font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0))
        val = ctk.CTkLabel(card, text="--", font=FONT_PULSE, text_color=color)
        val.pack(pady=20)
        self.cards[key] = val

    def refresh_data(self):
        try:
            # 1. Update Cards & Score
            stats = get_fleet_stats()
            for k, v in stats.items():
                self.cards[k].configure(text=str(v))
            
            total = sum(stats.values())
            score = int((stats["healthy"] / total) * 100) if total > 0 else 0
            self.score_label.configure(text=f"Health: {score}%")

            # 2. Update Progress Bars
            insights = get_system_insights()
            for w in self.main_content.winfo_children():
                if isinstance(w, ctk.CTkFrame): w.destroy()
            
            total_issues = sum(count for cat, count in insights)
            for cat, count in insights:
                row = ctk.CTkFrame(self.main_content, fg_color="transparent")
                row.pack(fill="x", padx=20, pady=5)
                ctk.CTkLabel(row, text=cat, font=FONT_BODY).pack(side="left")
                
                pct = (count / total_issues) if total_issues > 0 else 0
                bar_bg = ctk.CTkFrame(self.main_content, height=8, fg_color="#E0E0E0", corner_radius=4)
                bar_bg.pack(fill="x", padx=20, pady=(0, 10))
                ctk.CTkFrame(bar_bg, width=0, height=8, fg_color=G_BLUE, corner_radius=4).place(relwidth=pct, relheight=1)

            # 3. Update Activity Feed
            events = get_recent_activity()
            for w in self.feed_container.winfo_children(): w.destroy()
            for e in events:
                line = ctk.CTkFrame(self.feed_container, fg_color="#F8F9FA", corner_radius=6)
                line.pack(fill="x", pady=2)
                ctk.CTkLabel(line, text="●", text_color=e['color']).pack(side="left", padx=5)
                ctk.CTkLabel(line, text=f"{e['bid']}: {e['event']}", font=FONT_BODY).pack(side="left")

        except Exception as e:
            print(f"Refresh Error: {e}")