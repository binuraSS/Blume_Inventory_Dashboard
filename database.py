import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "test spreadsheet"
spreadsheet = client.open(SPREADSHEET_NAME)

# Sheet Definitions
inventory_sheet = spreadsheet.get_worksheet(0) # Sheet 1: Inventory
fault_sheet = spreadsheet.get_worksheet(1)     # Sheet 2: Active Faults
repair_sheet = spreadsheet.get_worksheet(2)    # Sheet 3: (Assuming this is your archive/Sheet 4)

def get_next_ticket_id():
    """Checks both active and archived sheets for the highest ID ever used."""
    prefix = "ID-"
    try:
        # Get Ticket IDs from Column A (index 1) of both sheets
        active_ids = fault_sheet.col_values(1)[1:]   # Skip header
        archive_ids = repair_sheet.col_values(1)[1:] # Skip header
        all_known_ids = active_ids + archive_ids
        
        if not all_known_ids:
            return f"{prefix}00001"

        # Extract digits using regex
        nums = []
        for tid in all_known_ids:
            found = re.findall(r'\d+', str(tid))
            if found:
                nums.append(int(found[0]))
        
        if not nums:
            return f"{prefix}00001"

        # Increment the highest number found
        next_id_num = max(nums) + 1
        return f"{prefix}{next_id_num:05d}"
    except Exception as e:
        print(f"ID Generation Error: {e}")
        return f"{prefix}99999" # Safety fallback

def add_device(blume_id, item, serial, date):
    inventory_sheet.append_row([blume_id, item, serial, date])

def report_fault(blume_id, status, notes):
    """Generates a globally unique ID and logs the fault to Sheet 2."""
    try:
        # Use the smart ID generator
        new_tid = get_next_ticket_id()
        issue_date = datetime.today().strftime("%Y-%m-%d")
        
        # Row format for Sheet 2: Ticket ID, Blume ID, Issue Date, Device Status, Issue Notes
        new_row = [new_tid, blume_id, issue_date, status, notes]
        
        fault_sheet.append_row(new_row)
        return new_tid
    except Exception as e:
        print(f"Error in report_fault: {e}")
        raise e

def archive_resolved_ticket(ticket_id, tech_notes):
    """Moves a ticket from Active (Sheet 2) to Archive (Sheet 3) with tech notes."""
    try:
        # 1. Fetch all data from active fault sheet
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

        # 2. Prepare data for Archive (Sheet 3)
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

        # 3. Append to Archive and Delete from Active
        repair_sheet.append_row(new_row)
        fault_sheet.delete_rows(row_index)
        return True
        
    except Exception as e:
        print(f"Database Error: {e}")
        return False

def search_device(query_value):
    """Searches inventory and active faults."""
    all_items = inventory_sheet.get_all_records()
    all_faults = fault_sheet.get_all_records()
    results = []
    query_lower = str(query_value).lower().strip()

    for item in all_items:
        bid = str(item.get('Blume ID', ''))
        
        # Filter faults for this specific device
        item_faults = [f for f in all_faults if str(f.get('Blume ID')) == bid]
        
        # Map Google Sheet headers to UI dictionary keys
        formatted_faults = [{
            "Ticket ID": f.get('Ticket ID', 'N/A'),
            "Issue Date": f.get('Issue Date', 'N/A'),
            "Status": f.get('Device Status', 'N/A'), # Key fixed here
            "Notes": f.get('Issue Notes', '')
        } for f in item_faults]

        # Use the mapped "Status" key for the search comparison
        match_in_faults = any(query_lower in str(f["Status"]).lower() for f in formatted_faults)

        if query_lower == bid.lower() or match_in_faults:
            results.append({
                "Blume ID": bid,
                "Item Category": item.get('Item Category', 'Unknown'),
                "Serial Number": item.get('Serial Number', 'N/A'),
                "Originated Date": item.get('Originated Date', 'N/A'),
                "issues": formatted_faults 
            })
    return results