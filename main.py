import customtkinter as ctk
from styles import *
# This looks into the views folder and pulls classes defined in __init__.py
from views import AddDeviceView, FaultReportView, SearchView, RepairView

class BlumeApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Blume Management Console")
        self.geometry("1150x850")
        self.configure(fg_color=G_WINDOW_BG)

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._init_sidebar()
        self._init_view_container()
        self._init_snackbar()

        # Initialize and Stack Frames
        self.frames = {}
        for F in (AddDeviceView, FaultReportView, SearchView, RepairView):
            # Views that need the snackbar get the show_msg callback
            if F in (AddDeviceView, FaultReportView, RepairView):
                frame = F(self.view_container, self.show_msg)
            else:
                frame = F(self.view_container)
            
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("AddDeviceView")

    def _init_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=280, fg_color=G_BG, corner_radius=0, border_width=1, border_color=G_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Blume", font=FONT_H1, text_color=G_BLUE).pack(pady=(50, 40))

        self.nav_btns = {}
        menu = [
            ("Add New Device", "AddDeviceView"),
            ("Search Inventory", "SearchView"),
            ("Report Fault", "FaultReportView"),
            ("Repair Center", "RepairView"),
            
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
        for btn_name, btn_obj in self.nav_btns.items():
            apply_material_button(btn_obj, "primary" if btn_name == name else "secondary")
        self.frames[name].tkraise()

    def show_msg(self, text):
        self.snackbar_label.configure(text=text)
        self.snackbar.place(relx=0.5, rely=0.92, anchor="s")
        self.after(3000, self.snackbar.place_forget)

if __name__ == "__main__":
    app = BlumeApp()
    app.mainloop()