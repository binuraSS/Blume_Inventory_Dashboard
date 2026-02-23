# main.py
import customtkinter as ctk
from styles import *
from views import AddDeviceView, FaultReportView, SearchView

class BlumeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. Window Configuration
        self.title("Blume Management Console")
        self.geometry("1150x850")
        self.configure(fg_color=G_WINDOW_BG)

        # 2. Main Grid Layout
        # Column 0: Sidebar | Column 1: Main Content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 3. Initialize UI Components
        self._init_sidebar()
        self._init_view_container()
        self._init_snackbar()

        # 4. Initialize Views (Frames)
        self.frames = {}
        for F in (AddDeviceView, FaultReportView, SearchView):
            # Pass the show_msg method to views that need to trigger the snackbar
            if F in (AddDeviceView, FaultReportView):
                frame = F(self.view_container, self.show_msg)
            else:
                frame = F(self.view_container)
            
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # 5. Set Default View
        self.show_frame("AddDeviceView")

    def _init_sidebar(self):
        """Builds the Material Design sidebar."""
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=G_BG, corner_radius=0, border_width=1, border_color=G_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo
        ctk.CTkLabel(self.sidebar, text="Blume", font=FONT_H1, text_color=G_BLUE).pack(pady=(50, 40))

        # Navigation Buttons
        self.nav_btns = {}

        # Button: Add Device
        btn_add = ctk.CTkButton(self.sidebar, text="  Add New Device", anchor="w", 
                                 command=lambda: self.show_frame("AddDeviceView"))
        apply_material_button(btn_add, "secondary")
        btn_add.pack(pady=5, padx=20, fill="x")
        self.nav_btns["AddDeviceView"] = btn_add

        # Button: Report Fault
        btn_fault = ctk.CTkButton(self.sidebar, text="  Report Fault", anchor="w", 
                                   command=lambda: self.show_frame("FaultReportView"))
        apply_material_button(btn_fault, "secondary")
        btn_fault.pack(pady=5, padx=20, fill="x")
        self.nav_btns["FaultReportView"] = btn_fault

        # Button: Search
        btn_search = ctk.CTkButton(self.sidebar, text="  Search Inventory", anchor="w", 
                                    command=lambda: self.show_frame("SearchView"))
        apply_material_button(btn_search, "secondary")
        btn_search.pack(pady=5, padx=20, fill="x")
        self.nav_btns["SearchView"] = btn_search

    def _init_view_container(self):
        """Creates the area where different views will be raised."""
        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.grid(row=0, column=1, sticky="nsew", padx=40, pady=20)
        self.view_container.grid_rowconfigure(0, weight=1)
        self.view_container.grid_columnconfigure(0, weight=1)

    def _init_snackbar(self):
        """Initializes the floating snackbar notification."""
        self.snackbar = ctk.CTkFrame(self, height=48, fg_color=G_TEXT, corner_radius=8)
        self.snackbar_label = ctk.CTkLabel(self.snackbar, text="", font=FONT_BODY, text_color="white")
        self.snackbar_label.pack(side="left", padx=20, pady=10)
        # We use place for the snackbar so it floats over content
        self.snackbar.place_forget()

    def show_frame(self, name):
        """Raises the selected frame and updates button styling."""
        # Update Nav Styles
        for btn_name, btn_obj in self.nav_btns.items():
            if btn_name == name:
                apply_material_button(btn_obj, "primary")
            else:
                apply_material_button(btn_obj, "secondary")

        # Raise Frame
        frame = self.frames[name]
        frame.tkraise()

    def show_msg(self, text):
        """Displays a snackbar message for 3 seconds."""
        self.snackbar_label.configure(text=text)
        self.snackbar.place(relx=0.5, rely=0.92, anchor="s")
        self.after(3000, self.snackbar.place_forget)

# --- Entry Point ---
if __name__ == "__main__":
    app = BlumeApp()
    app.mainloop()