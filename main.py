# Ensure these class names match exactly what is in your views/__init__.py
import customtkinter as ctk
# 1. ADD RoutineCheckView to your imports
from views import AddDeviceView, FaultReportView, SearchView, RepairView, DashboardView, RoutineCheckView
from styles import *

class BlumeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Blume Management Console")
        self.geometry("1200x850") # Slightly wider for the new table
        self.configure(fg_color=G_WINDOW_BG)

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._init_sidebar()
        self._init_view_container()
        self._init_snackbar()

        # Initialize and Stack Frames
        self.frames = {}
        
        # 2. UPDATE: Add RoutineCheckView to the lists
        # We define which views need the 'show_msg' callback
        views_needing_msg = (AddDeviceView, FaultReportView, RepairView, DashboardView, RoutineCheckView)
        
        # Add RoutineCheckView to the iteration tuple
        all_views = (DashboardView, RoutineCheckView, SearchView, RepairView, FaultReportView, AddDeviceView)
        
        for F in all_views:
            if F in views_needing_msg:
                frame = F(self.view_container, self.show_msg)
            else:
                frame = F(self.view_container)
            
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Start on the Overview
        self.show_frame("DashboardView")

    def _init_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=G_BG, corner_radius=0, border_width=1, border_color=G_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Blume", font=FONT_H1, text_color=G_BLUE).pack(pady=(50, 40))

        self.nav_btns = {}
        # 3. UPDATE: Add the "Routine Check" option to the menu
        menu = [
            ("🔭 Overview", "DashboardView"),      
            ("🗓️ Routine Check", "RoutineCheckView"), # New Tab
            ("🔍 Search & History", "SearchView"), 
            ("🛠️ Active Workshop", "RepairView"),  
            ("⚠️ Report Fault", "FaultReportView"),
            ("➕ Add New Device", "AddDeviceView"),
        ]

        for text, view_name in menu:
            btn = ctk.CTkButton(self.sidebar, text=f"  {text}", anchor="w", 
                                 command=lambda v=view_name: self.show_frame(v))
            apply_material_button(btn, "secondary")
            btn.pack(pady=5, padx=20, fill="x")
            self.nav_btns[view_name] = btn

    def _init_view_container(self):
        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.grid(row=0, column=1, sticky="nsew", padx=40, pady=20)
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

    def _init_snackbar(self):
        self.snackbar = ctk.CTkFrame(self, height=48, fg_color=G_TEXT, corner_radius=8)
        self.snackbar_label = ctk.CTkLabel(self.snackbar, text="", font=FONT_BODY, text_color="white")
        self.snackbar_label.pack(side="left", padx=20, pady=10)
        self.snackbar.place_forget()

    def show_frame(self, name):
        """Switches the visible frame and refreshes data if it's the Dashboard or Routine Check."""
        if name not in self.frames:
            print(f"Error: Frame {name} not found!")
            return

        for btn_name, btn_obj in self.nav_btns.items():
            apply_material_button(btn_obj, "primary" if btn_name == name else "secondary")
        
        # Bring the selected frame to the front
        self.frames[name].tkraise()
        
        # 4. UPDATE: Trigger refreshes for data-heavy views
        if name == "DashboardView":
            self.frames[name].refresh_data()
        elif name == "RoutineCheckView":
            self.frames[name].refresh() # Ensures the maintenance dates are fresh

    def show_msg(self, text, type="info"):
        # We can color the snackbar based on success/error if you like
        bg_color = "#059669" if type == "success" else G_TEXT
        self.snackbar.configure(fg_color=bg_color)
        
        self.snackbar_label.configure(text=text)
        self.snackbar.place(relx=0.5, rely=0.92, anchor="s")
        self.after(3000, self.snackbar.place_forget)

if __name__ == "__main__":
    app = BlumeApp()
    app.mainloop()