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
repair_sheet = spreadsheet.get_worksheet(2)

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

def resolve_ticket(ticket_id):
    """Finds the fault ticket ID in Sheet 2 and deletes that row."""
    try:
        # 1. Get all values from the fault sheet (Sheet 2)
        # Assuming your fault sheet is named 'fault_sheet'
        rows = fault_sheet.get_all_values() 
        
        # 2. Find the row index where the Ticket ID matches
        for index, row in enumerate(rows):
            if row[0] == ticket_id:
                # gspread is 1-indexed, so add 1 to the 0-based loop index
                fault_sheet.delete_rows(index + 1)
                return True
        return False
    except Exception as e:
        print(f"Error resolving ticket: {e}")
        return False

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

def archive_resolved_ticket(ticket_id, tech_notes):
    try:
        # 1. Fetch the original fault data from Sheet 2
        rows = fault_sheet.get_all_values()
        target_row = None
        row_index = -1
        
        for i, row in enumerate(rows):
            if row[0] == ticket_id:
                target_row = row
                row_index = i + 1
                break
        
        if not target_row:
            return False

        # 2. Prepare data for Sheet 4
        # Columns: Ticket ID, Blume ID, Issue Date, Device Status, Issue Notes, Issue Status, Tech Notes, Resolved Date
        resolved_date = datetime.today().strftime("%Y-%m-%d")
        new_row = [
            target_row[0], # Ticket ID
            target_row[1], # Blume ID
            target_row[2], # Issue Date
            target_row[3], # Device Status
            target_row[4], # Issue Notes
            "Resolved",    # Issue Status
            tech_notes,    # From GUI
            resolved_date  # Current Date
        ]

        # 3. Write to Sheet 4 and Delete from Sheet 2
        repair_sheet.append_row(new_row)
        fault_sheet.delete_rows(row_index)
        return True
        
    except Exception as e:
        print(f"Database Error: {e}")
        return False