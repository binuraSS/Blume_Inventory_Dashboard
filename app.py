import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import database  # Ensure database.py is in the same folder

# --- Google Material Design Palette ---
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

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#FFFFFF", border_width=1, border_color=G_BORDER)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="Blume", font=("Arial", 26, "bold"), text_color=G_BLUE).pack(pady=(30, 5), padx=25, anchor="w")
        ctk.CTkLabel(self.sidebar, text="Inventory System", font=("Arial", 12), text_color=G_SUBTEXT).pack(pady=(0, 30), padx=25, anchor="w")

        # Nav pill
        self.nav_btn = ctk.CTkButton(self.sidebar, text="  Operations", font=("Arial", 13, "bold"), 
                                     fg_color="#E8F0FE", text_color=G_BLUE, hover_color="#D2E3FC", 
                                     height=40, corner_radius=20, anchor="w")
        self.nav_btn.pack(pady=5, padx=15, fill="x")

    def _setup_main_area(self):
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        self.header = ctk.CTkLabel(self.main_area, text="Resource Management", font=("Arial", 22), text_color=G_TEXT)
        self.header.grid(row=0, column=0, pady=(30, 20), padx=40, sticky="w")

        # Material Tabs
        self.tabs = ctk.CTkTabview(self.main_area, fg_color=G_BG, segmented_button_selected_color=G_BLUE,
                                   text_color=G_TEXT, border_width=1, border_color=G_BORDER, corner_radius=8)
        self.tabs.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        
        self.tab_add = self.tabs.add("New Device")
        self.tab_error = self.tabs.add("Report Error")

        # Snackbar
        self.snackbar = ctk.CTkFrame(self.main_area, height=48, fg_color=G_TEXT, corner_radius=4)
        self.snackbar.grid(row=2, column=0, padx=40, pady=20, sticky="ew")
        self.snackbar_label = ctk.CTkLabel(self.snackbar, text="", font=("Arial", 12), text_color="white")
        self.snackbar_label.pack(side="left", padx=20)
        self.snackbar.grid_remove()

        self._setup_inventory_tab()
        self._setup_error_tab()

    def _setup_inventory_tab(self):
        # Sheet 1: Blume ID, Item, Serial, Originated Date (4 Columns)
        c = ctk.CTkFrame(self.tab_add, fg_color="transparent")
        c.pack(pady=40, expand=True)

        self.bid = self._create_input(c, "Blume ID", "B-1234")
        
        ctk.CTkLabel(c, text="Item Category", font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        self.item_menu = ctk.CTkOptionMenu(c, values=["VR Headset (HTC Vive)", "External Battery Pack", "Left Hand Remote", "Right Hand Remote"], 
                                           width=400, height=40, fg_color="#F1F3F4", button_color="#F1F3F4", text_color=G_TEXT)
        self.item_menu.pack(pady=5)

        self.sn = self._create_input(c, "Serial Number", "SN-XXXX-XXXX")
        self.sn.bind("<KeyRelease>", self._mask_serial)

        self.date = self._create_input(c, "Originated Date", "YYYY-MM-DD")
        self.date.insert(0, datetime.today().strftime("%Y-%m-%d"))

        self.add_btn = ctk.CTkButton(c, text="Create Resource", font=("Arial", 14, "bold"), 
                                     fg_color=G_BLUE, height=45, width=180, corner_radius=4, command=self._handle_add)
        self.add_btn.pack(pady=40, anchor="e")

    def _setup_error_tab(self):
        # Sheet 2: Blume ID, Date, Status, Notes (4 Columns)
        c = ctk.CTkFrame(self.tab_error, fg_color="transparent")
        c.pack(pady=40, expand=True)

        self.err_bid = self._create_input(c, "Device Blume ID", "Enter ID")
        
        ctk.CTkLabel(c, text="Update Status", font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        self.err_status = ctk.CTkOptionMenu(c, values=["In Repair", "Damaged", "Missing", "Service Required"], 
                                            width=400, height=40, fg_color="#F1F3F4", button_color="#F1F3F4", text_color=G_TEXT)
        self.err_status.pack(pady=5)

        ctk.CTkLabel(c, text="Observation Notes", font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        self.err_notes = ctk.CTkTextbox(c, width=400, height=120, border_color=G_BORDER, fg_color="#F1F3F4")
        self.err_notes.pack(pady=5)

        self.err_btn = ctk.CTkButton(c, text="Log Issue", font=("Arial", 14, "bold"), 
                                     fg_color=G_RED, height=45, width=180, corner_radius=4, command=self._handle_error)
        self.err_btn.pack(pady=40, anchor="e")

    def _create_input(self, parent, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold"), text_color=G_SUBTEXT).pack(pady=(15, 0), anchor="w")
        entry = ctk.CTkEntry(parent, width=400, height=40, placeholder_text=placeholder, fg_color="white", border_color=G_BORDER, text_color=G_TEXT)
        entry.pack(pady=5)
        return entry

    def _mask_serial(self, event):
        if event.keysym in ("BackSpace", "Delete"): return
        val = self.sn.get().upper().replace("-", "")
        if len(val) >= 2:
            self.sn.delete(0, "end")
            self.sn.insert(0, f"{val[:2]}-{val[2:12]}")

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
                # Matches your 4-parameter database.add_device
                database.add_device(self.bid.get(), self.item_menu.get(), self.sn.get(), self.date.get())
                msg = "Resource created successfully."
            else:
                # Matches your 3-parameter database.report_error
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