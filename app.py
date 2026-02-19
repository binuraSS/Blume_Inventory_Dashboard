import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import database

# --- Styling ---
BG_COLOR = "#0F0F0F"
SIDEBAR_COLOR = "#161616"
CARD_COLOR = "#1E1E1E"
ACCENT_BLUE = "#3D5AFE"
BORDER_COLOR = "#333333"

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BLUME | Management System")
        self.geometry("1000x750")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_content()

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="BLUME", font=("Arial", 28, "bold"), text_color=ACCENT_BLUE).pack(pady=40)
        
        # Navigation
        ctk.CTkButton(self.sidebar, text="Operations", fg_color=ACCENT_BLUE).pack(pady=10, padx=20, fill="x")
        self.status_text = ctk.CTkLabel(self.sidebar, text="Sheet2 Linked", text_color="gray70")
        self.status_text.pack(side="bottom", pady=20)

    def _build_main_content(self):
        self.main_container = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")

        # Tabview for Modern Navigation
        self.tabs = ctk.CTkTabview(
            self.main_container, 
            fg_color=CARD_COLOR, 
            segmented_button_selected_color=ACCENT_BLUE,
            border_width=1,
            border_color=BORDER_COLOR,
            corner_radius=20
        )
        self.tabs.pack(pady=40, padx=40, fill="both", expand=True)

        self.tab_add = self.tabs.add("New Device")
        self.tab_error = self.tabs.add("Report Error / Issue")

        self._setup_add_device_tab()
        self._setup_error_report_tab()

    # --- TAB 1: NEW DEVICE (SHEET 1) ---
    def _setup_add_device_tab(self):
        parent = self.tab_add
        self.bid_entry = self._create_input(parent, "Blume ID", "B-XXXX")
        
        ctk.CTkLabel(parent, text="Item Type", font=("Arial", 12, "bold")).pack(pady=(10,0))
        self.item_menu = ctk.CTkOptionMenu(parent, values=["VR Headset", "Battery", "Remote L", "Remote R"], width=350)
        self.item_menu.pack(pady=5)
        
        self.sn_entry = self._create_input(parent, "Serial Number", "SN-XXXX")
        self.date_entry = self._create_input(parent, "Service Date", "YYYY-MM-DD")
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        ctk.CTkButton(parent, text="REGISTER TO SHEET 1", fg_color=ACCENT_BLUE, height=45, width=220, 
                      command=self._handle_add).pack(pady=30)

    # --- TAB 2: ERROR REPORTING (SHEET 2) ---
    def _setup_error_report_tab(self):
        parent = self.tab_error
        self.err_bid = self._create_input(parent, "Blume ID", "ID of the faulty device")
        
        ctk.CTkLabel(parent, text="New Current Status", font=("Arial", 12, "bold")).pack(pady=(10,0))
        self.err_status = ctk.CTkOptionMenu(parent, values=["In Repair", "Damaged", "Missing", "Needs Service"], width=350, fg_color="#E74C3C")
        self.err_status.pack(pady=5)

        ctk.CTkLabel(parent, text="Notes / Error Description", font=("Arial", 12, "bold")).pack(pady=(10,0))
        self.err_notes = ctk.CTkTextbox(parent, width=400, height=120, fg_color="#121212", border_color=BORDER_COLOR)
        self.err_notes.pack(pady=5)

        ctk.CTkButton(parent, text="LOG TO SHEET 2", fg_color="#E74C3C", hover_color="#C0392B", height=45, width=220, 
                      command=self._handle_error).pack(pady=30)

    # --- Logic Helpers ---
    def _create_input(self, parent, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold")).pack(pady=(10, 0))
        entry = ctk.CTkEntry(parent, width=350, placeholder_text=placeholder, fg_color="#121212", border_color=BORDER_COLOR)
        entry.pack(pady=5)
        return entry

    def _handle_add(self):
        bid, item, sn, date = self.bid_entry.get(), self.item_menu.get(), self.sn_entry.get(), self.date_entry.get()
        if not bid or not sn:
            return messagebox.showwarning("Warning", "Please fill Blume ID and Serial.")
        
        threading.Thread(target=self._async_add, args=(bid, item, sn, date), daemon=True).start()

    def _async_add(self, bid, item, sn, date):
     try:
        database.add_device(bid, item, sn, date, "Active")
        self.after(0, lambda: [messagebox.showinfo("Success", "Device Registered!"), self.bid_entry.delete(0, 'end')])
     except Exception as e:
        # Note the 'e=e' below. This "locks" the current error into the lambda.
        self.after(0, lambda e=e: messagebox.showerror("Database Error", str(e)))

    def _handle_error(self):
        bid = self.err_bid.get()
        status = self.err_status.get()
        notes = self.err_notes.get("1.0", "end-1c")
        
        if not bid or not notes.strip():
            return messagebox.showwarning("Warning", "Please provide Blume ID and Notes.")

        threading.Thread(target=self._async_error, args=(bid, status, notes), daemon=True).start()

    def _async_error(self, bid, status, notes):
       try:
        database.report_error(bid, status, notes)
        self.after(0, lambda: [messagebox.showinfo("Logged", "Sheet 2 Updated!"), self.err_notes.delete("1.0", "end")])
       except Exception as e:
        # Bind e to the local scope of the lambda
        self.after(0, lambda e=e: messagebox.showerror("Database Error", str(e)))

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()