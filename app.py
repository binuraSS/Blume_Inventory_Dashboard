import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import database

# --- Styling ---
BG_COLOR = "#0F0F0F"
SIDEBAR_COLOR = "#141414"
CARD_COLOR = "#1A1A1A"
ACCENT_BLUE = "#3D5AFE"
BORDER_COLOR = "#2B2B2B"
SUCCESS_GREEN = "#2ECC71"
ERROR_RED = "#E74C3C"

class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BLUME | Inventory v2.1")
        self.geometry("1100x850")
        self.configure(fg_color=BG_COLOR)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._setup_sidebar()
        self._setup_main_area()

    def _setup_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        ctk.CTkLabel(self.sidebar, text="BLUME", font=("Arial", 28, "bold"), text_color=ACCENT_BLUE).pack(pady=40)
        ctk.CTkButton(self.sidebar, text="Operations", fg_color=ACCENT_BLUE, height=40).pack(pady=10, padx=20, fill="x")

    def _setup_main_area(self):
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Header
        ctk.CTkLabel(self.main_area, text="Inventory Dashboard", font=("Arial", 24, "bold")).grid(row=0, column=0, pady=(30, 10), padx=40, sticky="w")

        # Tabview (The Glass Card)
        self.tabs = ctk.CTkTabview(self.main_area, fg_color=CARD_COLOR, segmented_button_selected_color=ACCENT_BLUE, border_width=1, border_color=BORDER_COLOR)
        self.tabs.grid(row=1, column=0, padx=40, pady=10, sticky="nsew")
        
        self.tab_add = self.tabs.add("New Device")
        self.tab_error = self.tabs.add("Report Error")

        # Toast Feedback
        self.toast_bar = ctk.CTkFrame(self.main_area, height=45, fg_color="transparent", corner_radius=10)
        self.toast_bar.grid(row=2, column=0, padx=40, pady=(10, 20), sticky="ew")
        self.toast_label = ctk.CTkLabel(self.toast_bar, text="", font=("Arial", 12, "bold"))
        self.toast_label.pack(expand=True)

        self._setup_inventory_tab()
        self._setup_error_tab()

    # --- TAB: NEW DEVICE (Sheet 1) ---
    def _setup_inventory_tab(self):
        frame = ctk.CTkFrame(self.tab_add, fg_color="transparent")
        frame.pack(expand=True)

        self.bid_entry = self._create_field(frame, "Blume ID", "B-XXXX")
        
        ctk.CTkLabel(frame, text="Item Type", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        self.item_menu = ctk.CTkOptionMenu(frame, values=["VR Headset", "Battery", "Remote L", "Remote R"], width=350)
        self.item_menu.pack(pady=5)

        self.sn_entry = self._create_field(frame, "Serial Number", "SN-XXXX")
        self.sn_entry.bind("<KeyRelease>", self._mask_serial)

        self.date_entry = self._create_field(frame, "Service Date", "YYYY-MM-DD")
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        self.add_btn = ctk.CTkButton(frame, text="ADD TO SYSTEM", fg_color=ACCENT_BLUE, height=45, width=250, command=self._handle_add)
        self.add_btn.pack(pady=30)

    # --- TAB: REPORT ERROR (Sheet 2) ---
    def _setup_error_tab(self):
        frame = ctk.CTkFrame(self.tab_error, fg_color="transparent")
        frame.pack(expand=True)

        self.err_bid = self._create_field(frame, "Device Blume ID", "ID of the faulty device")
        
        ctk.CTkLabel(frame, text="Current Status", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        self.err_status = ctk.CTkOptionMenu(frame, values=["In Repair", "Damaged", "Missing", "Needs Service"], width=350, fg_color=ERROR_RED)
        self.err_status.pack(pady=5)

        ctk.CTkLabel(frame, text="Notes / Error Description", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        self.err_notes = ctk.CTkTextbox(frame, width=350, height=120, fg_color="#121212", border_color=BORDER_COLOR)
        self.err_notes.pack(pady=5)

        self.err_btn = ctk.CTkButton(frame, text="LOG ERROR TO SHEET 2", fg_color=ERROR_RED, height=45, width=250, command=self._handle_error)
        self.err_btn.pack(pady=30)

    # --- UI Helpers ---
    def _create_field(self, parent, label, placeholder):
        ctk.CTkLabel(parent, text=label, font=("Arial", 12, "bold")).pack(pady=(15, 0))
        entry = ctk.CTkEntry(parent, width=350, height=35, placeholder_text=placeholder, fg_color="#121212", border_color=BORDER_COLOR)
        entry.pack(pady=5)
        return entry

    def _mask_serial(self, event):
        if event.keysym in ("BackSpace", "Delete"): return
        val = self.sn_entry.get().upper().replace("-", "")
        if len(val) >= 2:
            self.sn_entry.delete(0, "end")
            self.sn_entry.insert(0, f"{val[:2]}-{val[2:12]}")

    def trigger_toast(self, message, is_error=False):
        color = ERROR_RED if is_error else SUCCESS_GREEN
        self.toast_bar.configure(fg_color=color)
        self.toast_label.configure(text=message)
        self.after(3500, lambda: self.toast_bar.configure(fg_color="transparent"))
        self.after(3500, lambda: self.toast_label.configure(text=""))

    # --- Submission Logic ---
    def _handle_add(self):
        bid, item, sn, date = self.bid_entry.get(), self.item_menu.get(), self.sn_entry.get(), self.date_entry.get()
        if not bid or not sn: return self.trigger_toast("Missing Fields!", True)
        
        self.add_btn.configure(state="disabled", text="Syncing...")
        threading.Thread(target=self._worker, args=("add", bid, item, sn, date), daemon=True).start()

    def _handle_error(self):
        bid = self.err_bid.get()
        status = self.err_status.get()
        notes = self.err_notes.get("1.0", "end-1c")
        if not bid or not notes.strip(): return self.trigger_toast("Missing Notes/ID!", True)

        self.err_btn.configure(state="disabled", text="Logging...")
        threading.Thread(target=self._worker, args=("error", bid, status, notes), daemon=True).start()

    def _worker(self, mode, *args):
        try:
            if mode == "add":
                database.add_device(*args, "Active")
                success_msg = "Device added to Sheet 1"
            else:
                database.report_error(*args)
                success_msg = "Error logged to Sheet 2"
            
            self.after(0, lambda: self.trigger_toast(success_msg))
            self.after(0, self._clear_all)
        except Exception as e:
            self.after(0, lambda e=e: self.trigger_toast(f"FAILED: {str(e)}", True))
        finally:
            self.after(0, lambda: self.add_btn.configure(state="normal", text="ADD TO SYSTEM"))
            self.after(0, lambda: self.err_btn.configure(state="normal", text="LOG ERROR TO SHEET 2"))

    def _clear_all(self):
        self.bid_entry.delete(0, 'end')
        self.sn_entry.delete(0, 'end')
        self.err_bid.delete(0, 'end')
        self.err_notes.delete("1.0", "end")

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()