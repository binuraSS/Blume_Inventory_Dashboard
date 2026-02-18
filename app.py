# app.py

import customtkinter as ctk
from tkinter import messagebox
from database import add_device
from datetime import datetime
import re

# -------------------------
# App Setup
# -------------------------

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Blume Inventory System")
app.geometry("800x600")
app.minsize(700, 550)

# -------------------------
# Validation Helpers
# -------------------------

def validate_date(date_str):
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def validate_blume_id(blume_id):
    # Alphanumeric only (barcode safe)
    return re.fullmatch(r"[A-Za-z0-9\-]+", blume_id) is not None

def validate_serial(serial):
    return len(serial) >= 4


# -------------------------
# Layout Containers
# -------------------------

main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True, padx=20, pady=20)

title_label = ctk.CTkLabel(
    main_frame,
    text="Blume Inventory Dashboard",
    font=("Arial", 28, "bold")
)
title_label.pack(pady=(10, 20))

form_frame = ctk.CTkFrame(main_frame, corner_radius=12)
form_frame.pack(fill="x", padx=40, pady=10)


# -------------------------
# Form Fields
# -------------------------

def create_label(text):
    return ctk.CTkLabel(form_frame, text=text, font=("Arial", 14))

def create_entry(placeholder):
    return ctk.CTkEntry(form_frame, width=400, placeholder_text=placeholder)

# Blume ID
create_label("Blume ID").pack(pady=(15, 5))
blume_id_entry = create_entry("Scan or Enter Barcode ID")
blume_id_entry.pack()

# -------------------------
# Item Dropdown
# -------------------------

ITEM_OPTIONS = [
    "VR Headset (HTC Vive)",
    "External Battery Pack",
    "Left Hand Remote",
    "Right Hand Remote"
]

create_label("Item").pack(pady=(15, 5))

item_dropdown = ctk.CTkOptionMenu(
    form_frame,
    values=ITEM_OPTIONS,
    width=400
)
item_dropdown.pack()
item_dropdown.set(ITEM_OPTIONS[0])

# Serial
create_label("Serial Number").pack(pady=(15, 5))
serial_entry = create_entry("Serial Number")
serial_entry.pack()

# Service Date
create_label("Last Service Date (YYYY-MM-DD)").pack(pady=(15, 5))
service_date_entry = create_entry("YYYY-MM-DD")
service_date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
service_date_entry.pack()

# Status Dropdown
create_label("Current Status").pack(pady=(15, 5))
status_dropdown = ctk.CTkOptionMenu(
    form_frame,
    values=["In Use", "Deployed", "In Repair"]
)
status_dropdown.pack(pady=(0, 15))
status_dropdown.set("In Use")


# -------------------------
# Real-Time Validation Styling
# -------------------------

def style_valid(entry):
    entry.configure(border_color="green")

def style_invalid(entry):
    entry.configure(border_color="red")

def style_default(entry):
    entry.configure(border_color=("gray50", "gray30"))

def live_validate(event=None):
    # Blume ID
    if validate_blume_id(blume_id_entry.get().strip()):
        style_valid(blume_id_entry)
    else:
        style_invalid(blume_id_entry)

    # Serial
    if validate_serial(serial_entry.get().strip()):
        style_valid(serial_entry)
    else:
        style_invalid(serial_entry)

    # Date
    if validate_date(service_date_entry.get().strip()):
        style_valid(service_date_entry)
    else:
        style_invalid(service_date_entry)


blume_id_entry.bind("<KeyRelease>", live_validate)
serial_entry.bind("<KeyRelease>", live_validate)
service_date_entry.bind("<KeyRelease>", live_validate)


# -------------------------
# Barcode Scanner Support
# -------------------------
# Most barcode scanners act as keyboard input + Enter

def barcode_submit(event):
    if event.keysym == "Return":
        handle_add()

blume_id_entry.bind("<Return>", barcode_submit)


# -------------------------
# Submit Handler
# -------------------------

def handle_add():
    blume_id = blume_id_entry.get().strip()
    item = item_dropdown.get()
    serial = serial_entry.get().strip()
    service_date = service_date_entry.get().strip()
    status = status_dropdown.get()

    if not validate_blume_id(blume_id):
        messagebox.showerror("Error", "Invalid Blume ID format.")
        return

    if not validate_serial(serial):
        messagebox.showerror("Error", "Serial number too short.")
        return

    if not validate_date(service_date):
        messagebox.showerror("Error", "Date must be YYYY-MM-DD.")
        return

    try:
        add_device(blume_id, item, serial, service_date, status)
        messagebox.showinfo("Success", "Device added successfully!")

        # Clear fields
        blume_id_entry.delete(0, "end")
        item_entry.delete(0, "end")
        serial_entry.delete(0, "end")
        service_date_entry.delete(0, "end")
        service_date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        status_dropdown.set("In Use")

        style_default(blume_id_entry)
        style_default(serial_entry)
        style_default(service_date_entry)

        blume_id_entry.focus()

    except Exception as e:
        messagebox.showerror("Error", str(e))


# -------------------------
# Buttons
# -------------------------

button_frame = ctk.CTkFrame(main_frame)
button_frame.pack(pady=20)

add_button = ctk.CTkButton(
    button_frame,
    text="Add Device",
    width=200,
    height=40,
    command=handle_add
)
add_button.pack()

# -------------------------
# Run App
# -------------------------

blume_id_entry.focus()
app.mainloop()