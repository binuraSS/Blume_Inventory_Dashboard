# database.py
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "test spreadsheet"
spreadsheet = client.open(SPREADSHEET_NAME)
inventory_sheet = spreadsheet.get_worksheet(0)
fault_sheet = spreadsheet.get_worksheet(1)

def generate_ticket_id():
    """Generates sequential ID-00001 format."""
    try:
        current_rows = fault_sheet.col_values(1)
        next_number = len(current_rows) 
        return f"ID-{next_number:05d}"
    except:
        return "ID-ERROR"

def add_device(blume_id, item, serial, date):
    inventory_sheet.append_row([blume_id, item, serial, date])

def report_fault(blume_id, status, notes):
    ticket_id = generate_ticket_id()
    new_row = [ticket_id, blume_id, datetime.today().strftime("%Y-%m-%d"), status, notes]
    fault_sheet.insert_row(new_row, 2)
    return ticket_id

def search_device(query_value):
    all_items = inventory_sheet.get_all_records()
    all_faults = fault_sheet.get_all_records()
    results = []
    query_lower = str(query_value).lower().strip()

    for item in all_items:
        bid = str(item.get('Blume ID', ''))
        item_faults = [f for f in all_faults if str(f.get('Blume ID')) == bid]
        
        # Format for UI
        formatted_faults = [{
            "Ticket ID": f.get('Ticket ID', 'N/A'),
            "Issue Date": f.get('Issue Date', 'N/A'),
            "Status": f.get('Device Status', 'N/A'),
            "Notes": f.get('Issue Notes', '')
        } for f in item_faults]

        if query_lower == bid.lower() or any(query_lower in str(f["Device Status"]).lower() for f in item_faults):
            results.append({
                "Blume ID": bid,
                "Item Category": item.get('Item Category', 'Unknown'),
                "Serial Number": item.get('Serial Number', 'N/A'),
                "Originated Date": item.get('Originated Date', 'N/A'),
                "issues": formatted_faults 
            })
    return results