import customtkinter as ctk
from styles import *
from data.stats import get_fleet_stats, get_system_insights, get_recent_activity, get_reliability_metrics

class DashboardView(ctk.CTkFrame):
    def __init__(self, master, show_msg_cb=None):
        super().__init__(master, fg_color="transparent")
        self.show_msg = show_msg_cb
        
      # --- 1. Header & Score (No changes here) ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header, text="Fleet Overview", font=FONT_H1, text_color= G_TEXT).pack(side="left")
        self.score_label = ctk.CTkLabel(header, text="Health: --%", font=FONT_H2, text_color=G_BLUE)
        self.score_label.pack(side="right")

        # --- 2. Pulse Cards (No changes here) ---
        self.card_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.card_frame.pack(fill="x")
        self.cards = {}
        self._create_card("Active Faulty Devices", G_RED, "broken")
        self._create_card("Devices with Maintenance Due", "#D97706", "overdue") 
        self._create_card("Active Healthy Fleet", "#059669", "healthy")

        # --- 3. Middle Content Area (Distribution & Activity) ---
        # REMOVED: expand=True to stop it from pushing the next row away
        # CHANGED: pady bottom from 20 to 5 to remove the "Big Padding"
        middle_row = ctk.CTkFrame(self, fg_color="transparent")
        middle_row.pack(fill="x", pady=(20, 5)) 
        middle_row.grid_columnconfigure(0, weight=3) 
        middle_row.grid_columnconfigure(1, weight=2) 

        # LEFT: Anatomy of Faults
        self.main_content = ctk.CTkFrame(middle_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.main_content.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(self.main_content, text="Issue Distribution (Per Category)", 
                     font=FONT_LABEL_BOLD, text_color="black").pack(pady=(15, 10), padx=25, anchor="w")
        self.bars_container = ctk.CTkFrame(self.main_content, fg_color="transparent")
        self.bars_container.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        # RIGHT: Activity Feed
        self.feed_box = ctk.CTkFrame(middle_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.feed_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(self.feed_box, text="Recent Activity", font=FONT_LABEL_BOLD, text_color="black").pack(pady=10)
        self.feed_container = ctk.CTkScrollableFrame(self.feed_box, fg_color="transparent", height=150) # Set height to keep it compact
        self.feed_container.pack(fill="both", expand=True, padx=10, pady=5)

        # --- 4. Reliability Row (MTTR & Lemons) ---
        # This is now "Attached" because middle_row isn't expanding anymore
        self.reliability_row = ctk.CTkFrame(self, fg_color="transparent")
        self.reliability_row.pack(fill="x", pady=(5, 20)) # Small top padding (5) to stay close
        self.reliability_row.grid_columnconfigure(0, weight=1)
        self.reliability_row.grid_columnconfigure(1, weight=1)

        # LEFT: MTTR Display
        self.mttr_box = ctk.CTkFrame(self.reliability_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.mttr_box.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(self.mttr_box, text="Avg. Device Downtime", font=FONT_LABEL_BOLD, text_color="black").pack(pady=(12, 0))
        self.mttr_val = ctk.CTkLabel(self.mttr_box, text="-- Days", font=("Arial", 28, "bold"), text_color=G_BLUE)
        self.mttr_val.pack(pady=(5, 12))

        # RIGHT: Recurring Issues (Lemons)
        self.lemon_box = ctk.CTkFrame(self.reliability_row, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        self.lemon_box.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(self.lemon_box, text="Recurring Issues (Top Lemons)", font=FONT_LABEL_BOLD, text_color="black").pack(pady=(10, 2))
        self.lemon_container = ctk.CTkFrame(self.lemon_box, fg_color="transparent")
        self.lemon_container.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        self.refresh_data()

    def _create_card(self, title, color, key):
        card = ctk.CTkFrame(self.card_frame, fg_color="white", corner_radius=12, border_width=1, border_color=G_BORDER)
        card.pack(side="left", fill="both", expand=True, padx=5)
        ctk.CTkLabel(card, text=title, font=FONT_LABEL, text_color=G_SUBTEXT).pack(pady=(15, 0))
        val = ctk.CTkLabel(card, text="--", font=("Arial", 32, "bold"), text_color=color)
        val.pack(pady=(5, 15))
        self.cards[key] = val

    def refresh_data(self):
        # 1. Update the Big Cards (Stats)
        try:
            stats = get_fleet_stats()
         #   print(f"DEBUG: Dashboard received stats: {stats}") # Check terminal for this!
            
            for k, v in stats.items():
                if k in self.cards: 
                    self.cards[k].configure(text=str(v))
            
            total_fleet = sum(stats.values())
            score = int((stats["healthy"] / total_fleet) * 100) if total_fleet > 0 else 0
            self.score_label.configure(text=f"Health: {score}%")
        except Exception as e:
            print(f"Stats Card Error: {e}")

        # 2. Update the Bar Chart (Insights)
        try:
            insights = get_system_insights() 
            self._render_fault_anatomy(insights)
        except Exception as e:
            print(f"Insights Chart Error: {e}")

        # 3. Update the Activity Feed
        try:
            events = get_recent_activity()
            for w in self.feed_container.winfo_children(): w.destroy()
            for e in events:
                row = ctk.CTkFrame(self.feed_container, fg_color="#F8F9FA", corner_radius=8)
                row.pack(fill="x", pady=3, padx=2)
                ctk.CTkFrame(row, width=6, height=6, corner_radius=3, fg_color=e.get('color', G_BLUE)).pack(side="left", padx=10)
                ctk.CTkLabel(row, text=f"{e.get('bid', '??')}: {e.get('event', 'Action')}", font=("Arial", 11), text_color="black").pack(side="left", pady=8)
        except Exception as e:
            print(f"Activity Feed Error: {e}")

        # 4. Update Reliability Section
        try:
            rel = get_reliability_metrics()
            self.mttr_val.configure(text=f"{rel['mttr']} Days")
            
            # Clear old lemon entries
            for w in self.lemon_container.winfo_children(): w.destroy()
            
            if not rel['lemons']:
                ctk.CTkLabel(self.lemon_container, text="No recurring issues detected.", font=("Arial", 11), text_color=G_SUBTEXT).pack()
            else:
                for item in rel['lemons']:
                    row = ctk.CTkFrame(self.lemon_container, fg_color="transparent")
                    row.pack(fill="x")
                    ctk.CTkLabel(row, text=f"⚠️ {item['bid']}", font=("Arial", 12, "bold")).pack(side="left")
                    ctk.CTkLabel(row, text=f"{item['count']} failures", font=("Arial", 11), text_color=G_RED).pack(side="right")
        except Exception as e:
            print(f"UI Reliability Refresh Error: {e}")

    def _render_fault_anatomy(self, insights):
        for w in self.bars_container.winfo_children(): w.destroy()
        
        total_issues = sum(count for label, count in insights)
        if total_issues == 0:
            ctk.CTkLabel(self.bars_container, text="All systems clear.", font=("Arial", 12), text_color=G_SUBTEXT).pack(pady=40)
            return

        bar_container = ctk.CTkFrame(self.bars_container, height=28, fg_color="#F1F5F9", corner_radius=14)
        bar_container.pack(fill="x", pady=(10, 25))
        
        # Color Map using your exact preferred phrasing
        issue_colors = {
            "Physical damage": G_RED,
            "Tracking error": "#8B5CF6",
            "Software Error": "#F59E0B"
        }

        curr_x = 0
        for label, count in insights:
            pct = count / total_issues
            # Convert to lowercase just for the 'check', not for the 'display'
            check_label = str(label).lower().strip()

            # Default to Blue
            color = G_BLUE
            
            # Use lowercase checks to ensure we catch variations in the Sheet data
            if "physical damage" in check_label: 
                color = issue_colors["Physical damage"]
            elif "tracking error" in check_label: 
                color = issue_colors["Tracking error"]
            elif "software error" in check_label: 
                color = issue_colors["Software Error"]

            seg = ctk.CTkFrame(bar_container, fg_color=color, corner_radius=0)
            seg.place(relx=curr_x, rely=0, relwidth=pct, relheight=1)
            curr_x += pct

        # Legend
        ctk.CTkLabel(self.bars_container, text="Detailed Breakdown", font=("Arial", 10, "bold"), text_color=G_SUBTEXT).pack(anchor="w", padx=5, pady=(0, 10))

        for label, count in insights:
            row = ctk.CTkFrame(self.bars_container, fg_color="transparent")
            row.pack(fill="x", pady=4)
            
            check_label = str(label).lower().strip()
            dot_color = G_BLUE
            if "physical damage" in check_label: dot_color = issue_colors["Physical damage"]
            elif "tracking error" in check_label: dot_color = issue_colors["Tracking error"]
            elif "software error" in check_label: dot_color = issue_colors["Software Error"]

            ctk.CTkFrame(row, width=10, height=10, corner_radius=5, fg_color=dot_color).pack(side="left", padx=(5, 10))
            
            # This uses the 'label' directly from your data, preserving your exact casing
            ctk.CTkLabel(row, text=label, font=("Arial", 12, "bold"), text_color="black").pack(side="left")
            ctk.CTkLabel(row, text=f"{count} Units", font=("Arial", 11), text_color=G_SUBTEXT).pack(side="right")