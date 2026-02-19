import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# -------------------------
# Google Sheets Setup
# -------------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "test spreadsheet"
spreadsheet = client.open(SPREADSHEET_NAME)

# Worksheets
inventory_sheet = spreadsheet.get_worksheet(0) # Sheet1: Main Inventory
error_sheet = spreadsheet.get_worksheet(1)     # Sheet2: Error Reporting

def add_device(blume_id, item, serial, service_date, status):
    """Adds a new device to Sheet1."""
    existing_ids = inventory_sheet.col_values(1)
    if blume_id in existing_ids:
        raise ValueError(f"Blume ID '{blume_id}' already exists.")
    
    inventory_sheet.append_row([blume_id, item, serial, service_date, status])

def report_error(blume_id, status, notes):
    """
    Logs an error/status change to Sheet2.
    Headings: Blume ID, Date, Current Status, Notes
    """
    # Verification: Ensure device exists in main inventory before reporting error
    existing_ids = inventory_sheet.col_values(1)
    if blume_id not in existing_ids:
        raise ValueError(f"ID '{blume_id}' not found in main inventory.")

    # Append to Sheet2
    error_sheet.append_row([
        blume_id, 
        datetime.today().strftime("%Y-%m-%d"), # Date
        status,                               # Current Status
        notes                                 # Notes
    ])