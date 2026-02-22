import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import database

# --- Theme Configuration ---
G_BLUE, G_RED = "#1A73E8", "#D93025"
G_BG, G_WINDOW_BG = "#FFFFFF", "#F8F9FA"
G_TEXT, G_SUBTEXT, G_BORDER = "#202124", "#5F6368", "#DADCE0"

ctk.set_appearance_mode("light")

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blume Management Console")
        self.geometry("1150x850")
        self.configure(fg_color=G_WINDOW_BG)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()
        self._show_view("add")

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=260, corner_radius=0, fg_color="#FFFFFF", border_width=1, border_color=G_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Blume", font=("Arial", 26, "bold"), text_color=G_BLUE).pack(pady=(30, 5), padx=25, anchor="w")
        ctk.CTkLabel(self.sidebar, text="Inventory System", font=("Arial", 12), text_color=G_SUBTEXT).pack(pady=(0, 30), padx=25, anchor="w")

        self.btn_nav_add = self._create_nav_btn("  Add New Device", "add")
        self.btn_nav_fault = self._create_nav_btn("  Report Fault", "fault")
        self.btn_nav_search = self._create_nav_btn("  Search Device", "search")

    def _create_nav_btn(self, text, view):
        btn = ctk.CTkButton(self.sidebar, text=text, font=("Arial", 13, "bold"), height=44, corner_radius=22, anchor="w", 
                            command=lambda: self._show_view(view))
        btn.pack(pady=5, padx=15, fill="x")
        return btn

    def _setup_main_area(self):
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        self.view_title = ctk.CTkLabel(self.main_area, text="Page Title", font=("Arial", 28), text_color=G_TEXT)
        self.view_title.grid(row=0, column=0, pady=(40, 20), padx=50, sticky="w")

        # Views
        self.frame_add = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)
        self.frame_fault = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)
        self.frame_search = ctk.CTkFrame(self.main_area, fg_color=G_BG, border_width=1, border_color=G_BORDER, corner_radius=12)

        self.snackbar = ctk.CTkFrame(self.main_area, height=48, fg_color=G_TEXT, corner_radius=4)
        self.snackbar.grid(row=2, column=0, padx=50, pady=20, sticky="ew")
        self.snackbar_label = ctk.CTkLabel(self.snackbar, text="", font=("Arial", 12), text_color="white")
        self.snackbar_label.pack(side="left", padx=20)
        self.snackbar.grid_remove()

        self._build_add_form()
        self._build_fault_form()
        self._build_search_view()

    def _show_view(self, view_name):
        for f in [self.frame_add, self.frame_fault, self.frame_search]: f.grid_forget()
        
        inactive = {"fg_color": "transparent", "text_color": G_TEXT, "hover_color": "#F1F3F4"}
        active = {"fg_color": "#E8F0FE", "text_color": G_BLUE, "hover_color": "#D2E3FC"}
        
        for b in [self.btn_nav_add, self.btn_nav_fault, self.btn_nav_search]: b.configure(**inactive)

        if view_name == "add":
            self.view_title.configure(text="New Device Registration")
            self.btn_nav_add.configure(**active)
            self.frame_add.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")
        elif view_name == "fault":
            self.view_title.configure(text="Device Fault Reporting")
            self.btn_nav_fault.configure(**active)
            self.frame_fault.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")
        elif view_name == "search":
            self.view_title.configure(text="Inventory Search")
            self.btn_nav_search.configure(**active)
            self.frame_search.grid(row=1, column=0, padx=50, pady=10, sticky="nsew")

    # --- FORM BUILDERS ---
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

    def _build_fault_form(self):
        c = ctk.CTkFrame(self.frame_fault, fg_color="transparent")
        c.pack(pady=60, expand=True)
        self.f_bid = self._create_input(c, "Device Blume ID", "Enter ID")
        self.f_status = self._create_dropdown(c, "Device Status", ["Physical damage ", "Tracking error ", "Software Error "])
        ctk.CTkLabel(c, text="Issue Notes", font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        self.f_notes = ctk.CTkTextbox(c, width=400, height=120, border_color=G_BORDER, border_width=2, fg_color="white")
        self.f_notes.pack(pady=5)
        self.f_btn = ctk.CTkButton(c, text="Log Fault", fg_color=G_RED, height=45, width=180, corner_radius=4, command=self._handle_fault)
        self.f_btn.pack(pady=40, anchor="e")

    def _build_search_view(self):
        p = ctk.CTkFrame(self.frame_search, fg_color="transparent")
        p.pack(fill="both", expand=True, padx=20, pady=20)
        bar = ctk.CTkFrame(p, fg_color="transparent")
        bar.pack(fill="x", pady=(0, 20))
        self.s_entry = ctk.CTkEntry(bar, placeholder_text="Search by ID or Fault...", width=400, height=42)
        self.s_entry.pack(side="left", padx=(0, 10))
        self.s_btn = ctk.CTkButton(bar, text="Search", fg_color=G_BLUE, height=42, width=100, command=self._handle_search)
        self.s_btn.pack(side="left")
        self.s_results = ctk.CTkScrollableFrame(p, fg_color="#F1F3F4", corner_radius=8)
        self.s_results.pack(fill="both", expand=True)

    # --- HELPERS ---
    def _create_input(self, parent, label, ph):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        e = ctk.CTkEntry(parent, width=400, height=42, placeholder_text=ph, fg_color="white", border_color=G_BORDER)
        e.pack(pady=5); return e

    def _create_dropdown(self, parent, label, values):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        m = ctk.CTkOptionMenu(parent, values=values, width=400, height=42, fg_color="#F1F3F4", button_color="#F1F3F4", text_color=G_TEXT)
        m.pack(pady=5); return m

    def _mask_serial(self, event):
        if event.keysym in ("BackSpace", "Delete"): return
        val = self.sn.get().upper().replace("-", "")
        if len(val) >= 2: self.sn.delete(0, "end"); self.sn.insert(0, f"{val[:2]}-{val[2:12]}")

    def show_msg(self, text):
        self.snackbar_label.configure(text=text); self.snackbar.grid()
        self.after(4000, self.snackbar.grid_remove)

    # --- THREADING ---
    def _handle_add(self):
        self.add_btn.configure(state="disabled"); threading.Thread(target=self._worker, args=("add",), daemon=True).start()

    def _handle_fault(self):
        self.f_btn.configure(state="disabled"); threading.Thread(target=self._worker, args=("fault",), daemon=True).start()

    def _handle_search(self):
        self.s_btn.configure(state="disabled"); threading.Thread(target=self._worker, args=("search",), daemon=True).start()

    def _worker(self, mode):
        try:
            if mode == "add":
                database.add_device(self.bid.get(), self.item_menu.get(), self.sn.get(), self.date.get())
                self.after(0, lambda: self.show_msg("Resource Created."))
            elif mode == "fault":
                tid = database.report_fault(self.f_bid.get(), self.f_status.get(), self.f_notes.get("1.0", "end-1c"))
                self.after(0, lambda: self.show_msg(f"Fault Logged: {tid}"))
            elif mode == "search":
                res = database.search_device(self.s_entry.get())
                self.after(0, lambda: self._display_results(res))
        except Exception as e: self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: [self.add_btn.configure(state="normal"), self.f_btn.configure(state="normal"), self.s_btn.configure(state="normal")])

    def _display_results(self, results):
        for w in self.s_results.winfo_children(): w.destroy()
        if not results:
            ctk.CTkLabel(self.s_results, text="No records found.").pack(pady=20); return
        
        for item in results:
            issues = item.get("issues", [])
            if not issues: self._create_row_card(item, None)
            else:
                for issue in issues: self._create_row_card(item, issue)

    def _create_row_card(self, item, issue=None):
        card = ctk.CTkFrame(self.s_results, fg_color="white", corner_radius=12, border_width=2, border_color=G_BORDER)
        card.pack(fill="x", pady=8, padx=10)
        
        accent = ctk.CTkFrame(card, width=6, fg_color=G_RED if issue else G_BLUE, corner_radius=0)
        accent.pack(side="left", fill="y")

        cont = ctk.CTkFrame(card, fg_color="transparent")
        cont.pack(side="left", fill="both", expand=True, padx=20, pady=15)

        # Header: ID + Ticket ID
        header_text = f"{item['Blume ID']}" + (f"  ({issue['Ticket ID']})" if issue else "")
        ctk.CTkLabel(cont, text=header_text, font=("Arial", 16, "bold")).pack(anchor="w")

        # Badge
        status_text = issue['Status'].upper() if issue else "OPERATIONAL"
        badge = ctk.CTkFrame(card, fg_color="#FDEDEC" if issue else "#E8F5E9", corner_radius=6)
        badge.place(relx=0.98, rely=0.2, anchor="ne")
        ctk.CTkLabel(badge, text=f" {status_text} ", font=("Arial", 10, "bold"), text_color=G_RED if issue else "#2E7D32").pack(pady=2)

        # Details
        det = f"{item['Item Category']} • SN: {item['Serial Number']} • Registered: {item['Originated Date']}"
        ctk.CTkLabel(cont, text=det, font=("Arial", 11), text_color=G_SUBTEXT).pack(anchor="w", pady=(2, 0))

        if issue:
            ctk.CTkFrame(cont, height=1, fg_color=G_BORDER).pack(fill="x", pady=10)
            ctk.CTkLabel(cont, text=f"Logged {issue['Issue Date']}: {issue['Notes']}", font=("Arial", 12), wraplength=600, justify="left").pack(anchor="w")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()