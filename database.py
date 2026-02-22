import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import random
import string

# --- Google Sheets Setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "test spreadsheet"
spreadsheet = client.open(SPREADSHEET_NAME)

inventory_sheet = spreadsheet.get_worksheet(0) # Sheet1
fault_sheet = spreadsheet.get_worksheet(1)     # Sheet2

def generate_ticket_id():
    """Generates a unique static ID like FLT-X829."""
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"FLT-{suffix}"

def add_device(blume_id, item, serial, originated_date):
    """Adds a new device to Sheet1."""
    existing_ids = inventory_sheet.col_values(1)
    if blume_id in existing_ids:
        raise ValueError(f"Blume ID '{blume_id}' already exists.")
    inventory_sheet.append_row([blume_id, item, serial, originated_date])

def report_fault(blume_id, status, notes):
    """Logs a fault to Sheet2 and inserts it at the top (Row 2)."""
    existing_ids = inventory_sheet.col_values(1)
    if blume_id not in existing_ids:
        raise ValueError(f"ID '{blume_id}' not found in main inventory.")

    ticket_id = generate_ticket_id()
    new_row = [
        ticket_id,
        blume_id, 
        datetime.today().strftime("%Y-%m-%d"),
        status,
        notes
    ]
    # Insert at Row 2 so latest is always visible at the top of the sheet
    fault_sheet.insert_row(new_row, 2)
    return ticket_id

def search_device(query_value):
    """Unified search for Blume ID or Fault Status."""
    all_items = inventory_sheet.get_all_records()
    all_faults = fault_sheet.get_all_records()
    
    results = []
    query_lower = str(query_value).lower().strip()

    for item in all_items:
        bid = str(item.get('Blume ID', ''))
        
        # Aggregate all faults for this specific Blume ID
        item_faults = []
        for f in all_faults:
            if str(f.get('Blume ID')) == bid:
                item_faults.append({
                    "Ticket ID": f.get('Fault reporting Ticket ID', 'N/A'),
                    "Issue Date": f.get('Issue Date', 'N/A'),
                    "Status": f.get('Device Status', 'N/A'),
                    "Notes": f.get('Issue Notes', '')
                })

        # Match logic
        id_match = query_lower == bid.lower()
        fault_match = any(query_lower in str(f["Status"]).lower() for f in item_faults)

        if id_match or fault_match:
            results.append({
                "Blume ID": bid,
                "Item Category": item.get('Item Category', 'Unknown'),
                "Serial Number": item.get('Serial Number', 'N/A'),
                "Originated Date": item.get('Originated Date', 'N/A'),
                "issues": item_faults 
            })
            
    return results