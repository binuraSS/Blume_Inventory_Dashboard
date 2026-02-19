# app.py

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import re

from database import add_device


# =====================================================
# App Configuration
# =====================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

APP_WIDTH = 800
APP_HEIGHT = 600


# =====================================================
# Validation Functions
# =====================================================

def validate_date(date_str: str) -> bool:
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def validate_blume_id(blume_id: str) -> bool:
    # Alphanumeric + dash (barcode safe)
    return re.fullmatch(r"[A-Za-z0-9\-]+", blume_id) is not None


def validate_serial(serial: str) -> bool:
    return len(serial) >= 4


# =====================================================
# UI Styling Helpers
# =====================================================

def style_valid(entry):
    entry.configure(border_color="green")


def style_invalid(entry):
    entry.configure(border_color="red")


def style_default(entry):
    entry.configure(border_color=("gray50", "gray30"))


# =====================================================
# Application Class
# =====================================================

class InventoryApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Blume Inventory System")
        self.geometry(f"{APP_WIDTH}x{APP_HEIGHT}")
        self.minsize(700, 550)

        self._build_ui()

    # -----------------------------
    # UI Construction
    # -----------------------------

    def _build_ui(self):

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self._build_header()
        self._build_form()
        self._build_buttons()

    def _build_header(self):

        title = ctk.CTkLabel(
            self.main_frame,
            text="Blume Inventory Dashboard",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=(10, 20))

    def _build_form(self):

        self.form_frame = ctk.CTkFrame(self.main_frame, corner_radius=12)
        self.form_frame.pack(fill="x", padx=40, pady=10)

        # -------- Blume ID --------
        self._create_label("Blume ID")
        self.blume_id_entry = self._create_entry("Scan or Enter Barcode ID")
        self.blume_id_entry.bind("<KeyRelease>", self._live_validate)
        self.blume_id_entry.bind("<Return>", self._barcode_submit)

        # -------- Item Dropdown --------
        self._create_label("Item")

        self.ITEM_OPTIONS = [
            "VR Headset (HTC Vive)",
            "External Battery Pack",
            "Left Hand Remote",
            "Right Hand Remote"
        ]

        self.item_dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            values=self.ITEM_OPTIONS,
            width=400
        )
        self.item_dropdown.pack()
        self.item_dropdown.set("Select Item Type")

        self.item_error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            text_color="red"
        )
        self.item_error_label.pack(pady=(3, 0))

        # -------- Serial --------
        self._create_label("Serial Number")
        self.serial_entry = self._create_entry("Serial Number")
        self.serial_entry.bind("<KeyRelease>", self._live_validate)

        # -------- Service Date --------
        self._create_label("Last Service Date (YYYY-MM-DD)")
        self.service_date_entry = self._create_entry("YYYY-MM-DD")
        self.service_date_entry.insert(
            0, datetime.today().strftime("%Y-%m-%d")
        )
        self.service_date_entry.bind("<KeyRelease>", self._live_validate)

        # -------- Status --------
        self._create_label("Current Status")

        self.status_dropdown = ctk.CTkOptionMenu(
            self.form_frame,
            values=["In Use", "Deployed", "In Repair"]
        )
        self.status_dropdown.pack(pady=(0, 15))
        self.status_dropdown.set("In Use")

        self.blume_id_entry.focus()

    def _build_buttons(self):

        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=20)

        add_button = ctk.CTkButton(
            button_frame,
            text="Add Device",
            width=200,
            height=40,
            command=self._handle_add
        )
        add_button.pack()

    # -----------------------------
    # Reusable Field Builders
    # -----------------------------

    def _create_label(self, text):
        label = ctk.CTkLabel(
            self.form_frame,
            text=text,
            font=("Arial", 14)
        )
        label.pack(pady=(15, 5))

    def _create_entry(self, placeholder):
        entry = ctk.CTkEntry(
            self.form_frame,
            width=400,
            placeholder_text=placeholder
        )
        entry.pack()
        return entry

    # -----------------------------
    # Real-Time Validation
    # -----------------------------

    def _live_validate(self, event=None):

        # Blume ID
        if validate_blume_id(self.blume_id_entry.get().strip()):
            style_valid(self.blume_id_entry)
        else:
            style_invalid(self.blume_id_entry)

        # Serial
        if validate_serial(self.serial_entry.get().strip()):
            style_valid(self.serial_entry)
        else:
            style_invalid(self.serial_entry)

        # Date
        if validate_date(self.service_date_entry.get().strip()):
            style_valid(self.service_date_entry)
        else:
            style_invalid(self.service_date_entry)

    # -----------------------------
    # Barcode Support
    # -----------------------------

    def _barcode_submit(self, event):
        if event.keysym == "Return":
            self._handle_add()

    # -----------------------------
    # Submit Handler
    # -----------------------------

    def _handle_add(self):

        blume_id = self.blume_id_entry.get().strip()
        item = self.item_dropdown.get()
        serial = self.serial_entry.get().strip()
        service_date = self.service_date_entry.get().strip()
        status = self.status_dropdown.get()

        self.item_error_label.configure(text="")

        # ---- Validation ----

        if not validate_blume_id(blume_id):
            messagebox.showerror("Error", "Invalid Blume ID format.")
            return

        if item == "Select Item Type":
            self.item_error_label.configure(
                text="Please select an item type"
            )
            return

        if not validate_serial(serial):
            messagebox.showerror("Error", "Serial number too short.")
            return

        if not validate_date(service_date):
            messagebox.showerror("Error", "Date must be YYYY-MM-DD.")
            return

        # ---- Database Insert ----

        try:
            add_device(blume_id, item, serial, service_date, status)

            messagebox.showinfo(
                "Success",
                "Device added successfully!"
            )

            self._reset_form()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -----------------------------
    # Reset Form
    # -----------------------------

    def _reset_form(self):

        self.blume_id_entry.delete(0, "end")
        self.serial_entry.delete(0, "end")
        self.service_date_entry.delete(0, "end")

        self.service_date_entry.insert(
            0, datetime.today().strftime("%Y-%m-%d")
        )

        self.item_dropdown.set("Select Item Type")
        self.status_dropdown.set("In Use")

        style_default(self.blume_id_entry)
        style_default(self.serial_entry)
        style_default(self.service_date_entry)

        self.blume_id_entry.focus()


# =====================================================
# Run Application
# =====================================================

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()