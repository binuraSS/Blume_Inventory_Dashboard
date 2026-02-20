import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import database

# --- Google Palette ---
G_BLUE = "#1A73E8"
G_BG = "#FFFFFF"
G_WINDOW_BG = "#F8F9FA"
G_TEXT = "#202124"
G_SUBTEXT = "#5F6368"
G_BORDER = "#DADCE0"
G_RED = "#D93025"

ctk.set_appearance_mode("light")

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blume Management Console")
        self.geometry("1100x850")
        self.configure(fg_color=G_WINDOW_BG)

        # Main Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()
        
        # Default view
        self._show_view("add")

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#FFFFFF", border_width=1, border_color=G_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Blume", font=("Arial", 26, "bold"), text_color=G_BLUE).pack(pady=(30, 5), padx=25, anchor="w")
        ctk.CTkLabel(self.sidebar, text="Inventory Management", font=("Arial", 12), text_color=G_SUBTEXT).pack(pady=(0, 30), padx=25, anchor="w")

        # Sidebar Nav Pills
        self.btn_nav_add = ctk.CTkButton(self.sidebar, text="  Add New Device", font=("Arial", 13, "bold"), 
                                         height=44, corner_radius=22, anchor="w", 
                                         command=lambda: self._show_view("add"))
        self.btn_nav_add.pack(pady=5, padx=15, fill="x")

        self.btn_nav_err = ctk.CTkButton(self.sidebar, text="  Report Error", font=("Arial", 13, "bold"), 
                                         height=44, corner_radius=22, anchor="w", 
                                         command=lambda: self._show_view("error"))
        self.btn_nav_err.pack(pady=5, padx=15, fill="x")

    def _setup_main_area(self):
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # 1. Dynamic Page Title (Top of Window)
        self.view_title = ctk.CTkLabel(self.main_area, text="Page Title", font=("Arial", 28), text_color=G_TEXT)
        self.view_title.grid(row=0, column=0, pady=(40, 20), padx=50, sticky="w")

        # 2. View Containers (White Cards)
        self.frame_add = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)
        self.frame_err = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)

        # Snackbar
        self.snackbar = ctk.CTkFrame(self.main_area, height=48, fg_color=G_TEXT, corner_radius=4)
        self.snackbar.grid(row=2, column=0, padx=50, pady=20, sticky="ew")
        self.snackbar_label = ctk.CTkLabel(self.snackbar, text="", font=("Arial", 12), text_color="white")
        self.snackbar_label.pack(side="left", padx=20)
        self.snackbar.grid_remove()

        self._build_add_form()
        self._build_error_form()

    def _show_view(self, view_name):
        """Switches the view and updates Sidebar/Title."""
        # Hide all
        self.frame_add.grid_forget()
        self.frame_err.grid_forget()

        # Reset buttons to inactive style
        inactive_style = {"fg_color": "transparent", "text_color": G_TEXT, "hover_color": "#F1F3F4"}
        active_style = {"fg_color": "#E8F0FE", "text_color": G_BLUE, "hover_color": "#D2E3FC"}

        self.btn_nav_add.configure(**inactive_style)
        self.btn_nav_err.configure(**inactive_style)

        if view_name == "add":
            self.view_title.configure(text="New Device Registration")
            self.btn_nav_add.configure(**active_style)
            self.frame_add.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")
        elif view_name == "error":
            self.view_title.configure(text="Device Error Reporting")
            self.btn_nav_err.configure(**active_style)
            self.frame_err.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")

    # --- BUILD FORMS (Same Logic as before, just in separate frames) ---
    def _build_add_form(self):
        c = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        c.pack(pady=60, expand=True)

        self.bid = self._create_input(c, "Blume ID", "B-1234")
        self.item_menu = self._create_dropdown(c, "Item Category", ["VR Headset", "Battery", "Remote L", "Remote R"])
        self.sn = self._create_input(c, "Serial Number", "SN-XXXX-XXXX")
        self.sn.bind("<KeyRelease>", self._mask_serial)
        self.date = self._create_input(c, "Originated Date", "YYYY-MM-DD")
        self.date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        self.add_btn = ctk.CTkButton(c, text="Create Resource", fg_color=G_BLUE, height=45, width=180, corner_radius=4, command=self._handle_add)
        self.add_btn.pack(pady=40, anchor="e")

    def _build_error_form(self):
        c = ctk.CTkFrame(self.frame_err, fg_color="transparent")
        c.pack(pady=60, expand=True)

        self.err_bid = self._create_input(c, "Device Blume ID", "Enter ID")
        self.err_status = self._create_dropdown(c, "Update Status", ["In Repair", "Damaged", "Missing", "Service Required"])
        
        ctk.CTkLabel(c, text="Observation Notes", font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        self.err_notes = ctk.CTkTextbox(c, width=400, height=120, border_color=G_BORDER, fg_color="white")
        self.err_notes.pack(pady=5)

        self.err_btn = ctk.CTkButton(c, text="Log Issue", fg_color=G_RED, height=45, width=180, corner_radius=4, command=self._handle_error)
        self.err_btn.pack(pady=40, anchor="e")

    # --- UI Helpers (Simplified) ---
    def _create_input(self, parent, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        entry = ctk.CTkEntry(parent, width=400, height=42, placeholder_text=placeholder, fg_color="white", border_color=G_BORDER, text_color=G_TEXT)
        entry.pack(pady=5)
        return entry

    def _create_dropdown(self, parent, label, values):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        menu = ctk.CTkOptionMenu(parent, values=values, width=400, height=42, fg_color="#F1F3F4", button_color="#F1F3F4", text_color=G_TEXT)
        menu.pack(pady=5)
        return menu

    # --- Database & Masking Logic (Preserved) ---
    def _mask_serial(self, event):
        if event.keysym in ("BackSpace", "Delete"): return
        val = self.sn.get().upper().replace("-", "")
        if len(val) >= 2:
            self.sn.delete(0, "end"); self.sn.insert(0, f"{val[:2]}-{val[2:12]}")

    def show_msg(self, text):
        self.snackbar_label.configure(text=text)
        self.snackbar.grid()
        self.after(4000, lambda: self.snackbar.grid_remove())

    def _handle_add(self):
        self.add_btn.configure(state="disabled", text="Creating...")
        threading.Thread(target=self._worker, args=("add",), daemon=True).start()

    def _handle_error(self):
        self.err_btn.configure(state="disabled", text="Logging...")
        threading.Thread(target=self._worker, args=("error",), daemon=True).start()

    def _worker(self, mode):
        try:
            if mode == "add":
                database.add_device(self.bid.get(), self.item_menu.get(), self.sn.get(), self.date.get())
                msg = "Resource created successfully."
            else:
                database.report_error(self.err_bid.get(), self.err_status.get(), self.err_notes.get("1.0", "end-1c"))
                msg = "Issue logged to Sheet 2."
            self.after(0, lambda: self.show_msg(msg))
            self.after(0, self._clear_all)
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.add_btn.configure(state="normal", text="Create Resource"))
            self.after(0, lambda: self.err_btn.configure(state="normal", text="Log Issue"))

    def _clear_all(self):
        self.bid.delete(0, 'end'); self.sn.delete(0, 'end')
        self.err_bid.delete(0, 'end'); self.err_notes.delete("1.0", "end")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()