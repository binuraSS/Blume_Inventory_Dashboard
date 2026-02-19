import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import re
import threading
import database

# --- Styling Constants ---
BG_COLOR = "#0F0F0F"        # Deep Black
SIDEBAR_COLOR = "#161616"   # Slightly lighter grey
CARD_COLOR = "#1E1E1E"      # Glass card base
ACCENT_BLUE = "#3D5AFE"     # Electric Blue
BORDER_COLOR = "#333333"    # Subtle "Glass" edge

# =====================================================
# Validation Logic (Preserved from your original)
# =====================================================
def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_blume_id(blume_id: str) -> bool:
    return re.fullmatch(r"[A-Za-z0-9\-]+", blume_id) is not None

def validate_serial(serial: str) -> bool:
    return len(serial) >= 4

# =====================================================
# Modern UI Application
# =====================================================
class InventoryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("BLUME | Inventory System")
        self.geometry("1000x700")
        ctk.set_appearance_mode("dark")

        # Configure Main Grid (Sidebar + Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_main_content()

    def _build_sidebar(self):
        """Creates the navigation sidebar."""
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=SIDEBAR_COLOR, border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo = ctk.CTkLabel(self.sidebar, text="BLUME", font=("Arial", 28, "bold"), text_color=ACCENT_BLUE)
        self.logo.pack(pady=40)

        # Navigation Buttons (Future tabs can be added here)
        self.btn_dashboard = ctk.CTkButton(self.sidebar, text="Dashboard", fg_color="transparent", border_width=1, border_color=ACCENT_BLUE, text_color="white")
        self.btn_dashboard.pack(pady=10, padx=20, fill="x")
        
        self.status_label = ctk.CTkLabel(self.sidebar, text="System Online", font=("Arial", 10), text_color="gray")
        self.status_label.pack(side="bottom", pady=20)

    def _build_main_content(self):
        """Creates the glassmorphism card area."""
        self.main_container = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")

        # Header Title
        self.header = ctk.CTkLabel(self.main_container, text="Device Registration", font=("Arial", 32, "bold"), text_color="white")
        self.header.pack(pady=(40, 10), padx=50, anchor="w")

        # Glass Card Container
        self.glass_card = ctk.CTkFrame(
            self.main_container, 
            fg_color=CARD_COLOR, 
            corner_radius=20, 
            border_width=1, 
            border_color=BORDER_COLOR
        )
        self.glass_card.pack(pady=20, padx=50, fill="both", expand=True)

        self._build_form()

    def _build_form(self):
        """Builds the actual input fields inside the glass card."""
        
        # --- Blume ID ---
        self.blume_id_entry = self._create_input_group("Blume ID (Barcode)", "Scan ID here...")
        
        # --- Item Dropdown ---
        ctk.CTkLabel(self.glass_card, text="Item Type", font=("Arial", 13, "bold"), text_color="#AAAAAA").pack(pady=(15, 0))
        self.item_dropdown = ctk.CTkOptionMenu(
            self.glass_card,
            values=["VR Headset (HTC Vive)", "External Battery Pack", "Left Hand Remote", "Right Hand Remote"],
            width=400, height=40, fg_color="#2A2A2A", button_color=ACCENT_BLUE, dropdown_fg_color="#1E1E1E"
        )
        self.item_dropdown.pack(pady=5)
        self.item_dropdown.set("Select Item Type")

        # --- Serial ---
        self.serial_entry = self._create_input_group("Serial Number", "Enter S/N")

        # --- Date ---
        self.date_entry = self._create_input_group("Service Date", "YYYY-MM-DD")
        self.date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))

        # --- Status ---
        ctk.CTkLabel(self.glass_card, text="Initial Status", font=("Arial", 13, "bold"), text_color="#AAAAAA").pack(pady=(15, 0))
        self.status_dropdown = ctk.CTkOptionMenu(
            self.glass_card,
            values=["In Use", "Deployed", "In Repair"],
            width=400, height=40, fg_color="#2A2A2A", button_color="#444444"
        )
        self.status_dropdown.pack(pady=5)

        # --- Submit Button ---
        self.submit_btn = ctk.CTkButton(
            self.glass_card, text="ADD TO INVENTORY", 
            font=("Arial", 14, "bold"), fg_color=ACCENT_BLUE, 
            hover_color="#536DFE", height=50, width=300,
            command=self._handle_submit
        )
        self.submit_btn.pack(pady=40)

    def _create_input_group(self, label_text, placeholder):
        """Helper to create a label and entry pair quickly."""
        ctk.CTkLabel(self.glass_card, text=label_text, font=("Arial", 13, "bold"), text_color="#AAAAAA").pack(pady=(15, 0))
        entry = ctk.CTkEntry(
            self.glass_card, width=400, height=40, 
            placeholder_text=placeholder, fg_color="#121212", border_color=BORDER_COLOR
        )
        entry.pack(pady=5)
        return entry

    def _handle_submit(self):
        """Validates and triggers the database thread."""
        bid = self.blume_id_entry.get().strip()
        item = self.item_dropdown.get()
        sn = self.serial_entry.get().strip()
        date = self.date_entry.get().strip()
        status = self.status_dropdown.get()

        # Validation logic
        if not validate_blume_id(bid):
            return messagebox.showerror("Error", "Invalid Blume ID format.")
        if item == "Select Item Type":
            return messagebox.showerror("Error", "Please select an item type.")
        if not validate_serial(sn):
            return messagebox.showerror("Error", "Serial number must be 4+ characters.")
        if not validate_date(date):
            return messagebox.showerror("Error", "Date must be YYYY-MM-DD.")

        # Visual feedback: Disable button while processing
        self.submit_btn.configure(state="disabled", text="SYNCING TO CLOUD...")
        
        # Run DB call in background thread so UI doesn't hang
        thread = threading.Thread(target=self._run_db_upload, args=(bid, item, sn, date, status), daemon=True)
        thread.start()

    def _run_db_upload(self, bid, item, sn, date, status):
        """Background worker for Google Sheets."""
        try:
            database.add_device(bid, item, sn, date, status)
            self.after(0, self._on_upload_success)
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Database Error", str(e)))
            self.after(0, lambda: self.submit_btn.configure(state="normal", text="ADD TO INVENTORY"))

    def _on_upload_success(self):
        """Updates UI on successful upload."""
        self.submit_btn.configure(state="normal", text="ADD TO INVENTORY")
        messagebox.showinfo("Success", "Device logged successfully!")
        # Reset form
        self.blume_id_entry.delete(0, 'end')
        self.serial_entry.delete(0, 'end')
        self.blume_id_entry.focus()

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()