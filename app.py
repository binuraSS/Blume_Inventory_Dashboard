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

        self.btn_nav_search = ctk.CTkButton(self.sidebar, text="  Search Device", font=("Arial", 13, "bold"), 
                                         height=44, corner_radius=22, anchor="w", 
                                         command=lambda: self._show_view("search"))
        self.btn_nav_search.pack(pady=5, padx=15, fill="x")

    def _setup_main_area(self):
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # 1. Dynamic Page Title
        self.view_title = ctk.CTkLabel(self.main_area, text="Page Title", font=("Arial", 28), text_color=G_TEXT)
        self.view_title.grid(row=0, column=0, pady=(40, 20), padx=50, sticky="w")

        # 2. View Containers (Frame Switching happens here)
        self.frame_add = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)
        self.frame_err = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)
        self.frame_search = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)

        # Snackbar
        self.snackbar = ctk.CTkFrame(self.main_area, height=48, fg_color=G_TEXT, corner_radius=4)
        self.snackbar.grid(row=2, column=0, padx=50, pady=20, sticky="ew")
        self.snackbar_label = ctk.CTkLabel(self.snackbar, text="", font=("Arial", 12), text_color="white")
        self.snackbar_label.pack(side="left", padx=20)
        self.snackbar.grid_remove()

        self._build_add_form()
        self._build_error_form()
        self._build_search_view()

    def _show_view(self, view_name):
        """Switches the view and updates Sidebar/Title."""
        # Hide all frames
        self.frame_add.grid_forget()
        self.frame_err.grid_forget()
        self.frame_search.grid_forget()

        # Styles
        inactive_style = {"fg_color": "transparent", "text_color": G_TEXT, "hover_color": "#F1F3F4"}
        active_style = {"fg_color": "#E8F0FE", "text_color": G_BLUE, "hover_color": "#D2E3FC"}

        # Reset all buttons
        self.btn_nav_add.configure(**inactive_style)
        self.btn_nav_err.configure(**inactive_style)
        self.btn_nav_search.configure(**inactive_style)

        if view_name == "add":
            self.view_title.configure(text="New Device Registration")
            self.btn_nav_add.configure(**active_style)
            self.frame_add.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")
        elif view_name == "error":
            self.view_title.configure(text="Device Error Reporting")
            self.btn_nav_err.configure(**active_style)
            self.frame_err.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")
        elif view_name == "search":
            self.view_title.configure(text="Inventory Search")
            self.btn_nav_search.configure(**active_style)
            self.frame_search.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")

    def _build_search_view(self):
        """Builds the search interface."""
        parent = ctk.CTkFrame(self.frame_search, fg_color="transparent")
        parent.pack(fill="both", expand=True, padx=20, pady=20)

        # Search bar area
        search_bar = ctk.CTkFrame(parent, fg_color="transparent")
        search_bar.pack(fill="x", pady=(0, 20))

        self.search_entry = ctk.CTkEntry(search_bar, placeholder_text="Search by Blume ID or Error Name...", width=400, height=42)
        self.search_entry.pack(side="left", padx=(0, 10))

        self.search_btn = ctk.CTkButton(search_bar, text="Search", fg_color=G_BLUE, height=42, width=100, command=self._handle_search)
        self.search_btn.pack(side="left")

        # Results area (Scrollable)
        self.search_results_area = ctk.CTkScrollableFrame(parent, fg_color="#F1F3F4", corner_radius=8)
        self.search_results_area.pack(fill="both", expand=True)

    def _build_add_form(self):
        c = ctk.CTkFrame(self.frame_add, fg_color="transparent")
        c.pack(pady=60, expand=True)

        self.bid = self._create_input(c, "Blume ID", "B-1234")
        self.item_menu = self._create_dropdown(c, "Item Category", ["VR Headset (HTC Vive)", "External Battery Pack", "Left Hand Remote", "Right Hand Remote"])
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
        self.err_status = self._create_dropdown(c, "Update Status", ["Physical damage ", "Tracking error ", "Software Error "])
        
        ctk.CTkLabel(c, text="Observation Notes", font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        self.err_notes = ctk.CTkTextbox(c, width=400, height=120, border_color=G_BORDER, border_width=2, fg_color="white")
        self.err_notes.pack(pady=5)

        self.err_btn = ctk.CTkButton(c, text="Log Issue", fg_color=G_RED, height=45, width=180, corner_radius=4, command=self._handle_error)
        self.err_btn.pack(pady=40, anchor="e")

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

    def _handle_search(self):
        self.search_btn.configure(state="disabled", text="Searching...")
        threading.Thread(target=self._worker, args=("search",), daemon=True).start()

    def _worker(self, mode):
        try:
            if mode == "add":
                database.add_device(self.bid.get(), self.item_menu.get(), self.sn.get(), self.date.get())
                msg = "Resource created successfully."
                self.after(0, lambda: self.show_msg(msg))
                self.after(0, self._clear_all)
            elif mode == "error":
                database.report_error(self.err_bid.get(), self.err_status.get(), self.err_notes.get("1.0", "end-1c"))
                msg = "Issue logged to Sheet 2."
                self.after(0, lambda: self.show_msg(msg))
                self.after(0, self._clear_all)
            elif mode == "search":
                # Assuming search_device returns a list of devices with an 'issues' key
                query = self.search_entry.get()
                results = database.search_device(query) # You need to implement this in database.py
                self.after(0, lambda: self._display_search_results(results))
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.add_btn.configure(state="normal", text="Create Resource"))
            self.after(0, lambda: self.err_btn.configure(state="normal", text="Log Issue"))
            self.after(0, lambda: self.search_btn.configure(state="normal", text="Search"))

    def _display_search_results(self, results):
        """Renders search results as individual, pronounced row cards."""
        # Clear previous search
        for widget in self.search_results_area.winfo_children():
            widget.destroy()

        if not results:
            ctk.CTkLabel(self.search_results_area, text="No records found.", font=("Arial", 14)).pack(pady=20)
            return

        for item in results:
            # If a device has multiple issues, we create a card for EACH issue 
            # so they appear as individual rows in the search container.
            
            issues = item.get("issues", [])
            
            # Case: Device found but has no issues logged yet
            if not issues:
                self._create_row_card(item, None)
            
            # Case: Device has issues - create a card for every single one
            else:
                for issue in issues:
                    self._create_row_card(item, issue)

    def _create_row_card(self, item, issue=None):
        """Helper to create a high-visibility single row card."""
        # Main Card Container
        card = ctk.CTkFrame(self.search_results_area, fg_color="white", corner_radius=12, 
                            border_width=2, border_color=G_BORDER)
        card.pack(fill="x", pady=10, padx=10)

        # Left Accent Color Bar (Red if there's an error, Blue if it's just info)
        accent_color = G_RED if issue else G_BLUE
        accent_bar = ctk.CTkFrame(card, width=6, fg_color=accent_color, corner_radius=0)
        accent_bar.pack(side="left", fill="y")

        # Content Container
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        # Top Row: Blume ID and Status Badge
        top_line = ctk.CTkFrame(content, fg_color="transparent")
        top_line.pack(fill="x")

        ctk.CTkLabel(top_line, text=item['Blume ID'], font=("Arial", 18, "bold"), text_color=G_TEXT).pack(side="left")
        
        status_text = issue['Status'].upper() if issue else "OPERATIONAL"
        status_bg = "#FDEDEC" if issue else "#E8F5E9"
        status_fg = G_RED if issue else "#2E7D32"

        badge = ctk.CTkFrame(top_line, fg_color=status_bg, corner_radius=6)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text=f"  {status_text}  ", font=("Arial", 11, "bold"), text_color=status_fg).pack(pady=2)

        # Middle Row: Item Details
        details = f"{item['Item Category']}  •  SN: {item['Serial Number']}  •  Registered: {item['Originated Date']}"
        ctk.CTkLabel(content, text=details, font=("Arial", 12), text_color=G_SUBTEXT).pack(anchor="w", pady=(5, 0))

        # Bottom Row: Notes (Only if issue exists)
        if issue:
            separator = ctk.CTkFrame(content, height=1, fg_color=G_BORDER)
            separator.pack(fill="x", pady=10)
            
            note_text = f"Logged on {issue['Issue Date']}: {issue['Notes']}"
            ctk.CTkLabel(content, text=note_text, font=("Arial", 13), text_color=G_TEXT, 
                         wraplength=700, justify="left").pack(anchor="w")

    def _clear_all(self):
        self.bid.delete(0, 'end'); self.sn.delete(0, 'end')
        self.err_bid.delete(0, 'end'); self.err_notes.delete("1.0", "end")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()