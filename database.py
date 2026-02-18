# database.py

import http
import gspread
from google.oauth2.service_account import Credentials

# -------------------------
# Google Sheets Setup
# -------------------------

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(creds)

# Replace with your exact spreadsheet name
SPREADSHEET_NAME = "Blume Inventory"

sheet = client.open("test spreadsheet").worksheet("Sheet1")


# -------------------------
# Add Device
# -------------------------

def add_device(blume_id, item, serial, service_date, status):
    if not all([blume_id, item, serial, service_date, status]):
        raise ValueError("All fields are required.")

    # Check if Blume ID already exists
    records = sheet.get_all_records()
    for row in records:
        if row["Blume ID"] == blume_id:
            raise ValueError("Blume ID already exists.")

    sheet.append_row([
        blume_id,
        item,
        serial,
        service_date,
        status
    ])


# -------------------------
# Update Status
# -------------------------

def update_status(blume_id, new_status):
    cell = sheet.find(blume_id)

    if not cell:
        raise ValueError("Device not found.")

    status_column = 5  # Current Status column
    sheet.update_cell(cell.row, status_column, new_status)


# -------------------------
# Add Service Note (Optional future expansion placeholder)
# -------------------------

def add_service_note(blume_id, note):
    # You can expand this later to use a Service_Logs worksheet
    raise NotImplementedError("Service log feature not implemented yet.")