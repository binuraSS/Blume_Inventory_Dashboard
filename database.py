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

def add_device(blume_id, item, serial, originated_date):
    """Adds a new device to Sheet1."""
    existing_ids = inventory_sheet.col_values(1)
    if blume_id in existing_ids:
        raise ValueError(f"Blume ID '{blume_id}' already exists.")
    
    inventory_sheet.append_row([blume_id, item, serial, originated_date])

def report_error(blume_id, status, notes):
    """Logs an error/status change to Sheet2."""
    existing_ids = inventory_sheet.col_values(1)
    if blume_id not in existing_ids:
        raise ValueError(f"ID '{blume_id}' not found in main inventory.")

    error_sheet.append_row([
        blume_id, 
        datetime.today().strftime("%Y-%m-%d"),
        status,
        notes
    ])

def search_device(query_value):
    """
    Unified search that checks for Blume ID or Error Type.
    Returns a list of dictionaries structured for the UI.
    """
    # Get all records from both sheets
    all_items = inventory_sheet.get_all_records()
    all_errors = error_sheet.get_all_records()
    
    results = []
    query_lower = str(query_value).lower().strip()
    # Reverse the errors list so the newest entries are processed first
    all_errors.reverse()

    for item in all_items:
        # 1. Extract basic info
        bid = str(item.get('Blume ID', ''))
        category = item.get('Item Category', 'Unknown')
        serial = item.get('Serial Number', 'N/A')
        date = item.get('Originated Date', 'N/A')

        # 2. Find all errors linked to this Blume ID
        # Note: Ensure these keys match your Google Sheet headers exactly!
        item_errors = []
        for e in all_errors:
            if str(e.get('Blume ID')) == bid:
                item_errors.append({
                    "Date": e.get('Date', 'N/A'),
                    "Status": e.get('Status', 'N/A'),
                    "Notes": e.get('Notes', '')
                })

        # 3. Determine if this item matches the search query
        # Matches if: Query is the Blume ID OR Query matches an error status
        id_match = query_lower == bid.lower()
        error_match = any(query_lower in str(err["Status"]).lower() for err in item_errors)

        if id_match or error_match:
            results.append({
                "Blume ID": bid,
                "Item Category": category,
                "Serial Number": serial,
                "Originated Date": date,
                "issues": item_errors # This is the list the UI loops through
            })
            
    return results