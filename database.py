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
repair_sheet = spreadsheet.get_worksheet(2)    # Sheet 3/4: Archive

# --- SYNC & MAINTENANCE LOGIC ---

def update_last_service(blume_id):
    """Updates the 'Last Service' column (Col E / 5) in the Inventory sheet."""
    try:
        cell = inventory_sheet.find(str(blume_id))
        if cell:
            today = datetime.today().strftime("%Y-%m-%d")
            # Update Column 5 (E)
            inventory_sheet.update_cell(cell.row, 5, today)
            return True
    except Exception as e:
        print(f"Sync Error: {e}")
        return False

def get_maintenance_status(blume_id):
    """Calculates if 180 days have passed since Column E's date."""
    try:
        cell = inventory_sheet.find(str(blume_id))
        # Get value from Column E
        last_service_val = inventory_sheet.cell(cell.row, 5).value
        
        if not last_service_val or last_service_val == "N/A":
            return "No Service History", "#F1C40F"

        last_date = datetime.strptime(last_service_val, "%Y-%m-%d")
        days_since = (datetime.now() - last_date).days
        
        if days_since >= 1:
            return f"Maintenance Overdue ({days_since} days)", "#F1C40F"
        return "Up to Date", "#27AE60"
    except:
        return "Status Unknown", "gray"

# --- CORE FUNCTIONS (RESTORED & UPDATED) ---

def add_device(blume_id, item, serial, date):
    """Adds new device to Sheet 1. Also sets the initial 'Last Service' to the creation date."""
    # Row: Blume ID, Item, Serial, Originated Date, Last Service (Sync Column)
    inventory_sheet.append_row([blume_id, item, serial, date, date])

def report_fault(blume_id, status, notes):
    """Generates a globally unique ID and logs the fault to Sheet 2."""
    try:
        new_tid = get_next_ticket_id()
        issue_date = datetime.today().strftime("%Y-%m-%d")
        new_row = [new_tid, blume_id, issue_date, status, notes]
        fault_sheet.append_row(new_row)
        return new_tid
    except Exception as e:
        print(f"Error in report_fault: {e}")
        raise e

def archive_resolved_ticket(ticket_id, tech_notes):
    """Moves ticket to Archive and updates the service clock on Sheet 1."""
    try:
        rows = fault_sheet.get_all_values()
        target_row = None
        row_index = -1
        
        for i, row in enumerate(rows):
            if row[0] == ticket_id:
                target_row = row
                row_index = i + 1
                break
        
        if not target_row: return False

        resolved_date = datetime.today().strftime("%Y-%m-%d")
        new_row = [
            target_row[0], target_row[1], target_row[2], 
            target_row[3], target_row[4], "Resolved",    
            tech_notes, resolved_date  
        ]

        repair_sheet.append_row(new_row)
        fault_sheet.delete_rows(row_index)
        
        # Sync the first sheet
        update_last_service(target_row[1]) 
        return True
    except Exception as e:
        print(f"Database Error: {e}")
        return False

def mark_as_inspected(blume_id, tech_name="Admin"):
    """Resets the 180-day clock by updating Sheet 1 and adding an Archive log."""
    try:
        new_tid = get_next_ticket_id()
        today = datetime.today().strftime("%Y-%m-%d")
        inspection_entry = [
            new_tid, blume_id, today, "Healthy", 
            "Routine Check", "Inspected", f"Inspected by {tech_name}", today
        ]
        repair_sheet.append_row(inspection_entry)
        return update_last_service(blume_id)
    except Exception as e:
        print(f"Inspection Error: {e}")
        return False

# --- UTILITY FUNCTIONS ---

def get_next_ticket_id():
    prefix = "ID-"
    try:
        active_ids = fault_sheet.col_values(1)[1:]   
        archive_ids = repair_sheet.col_values(1)[1:] 
        all_known_ids = active_ids + archive_ids
        if not all_known_ids: return f"{prefix}00001"
        nums = [int(f[0]) for tid in all_known_ids if (f := re.findall(r'\d+', str(tid)))]
        return f"{prefix}{max(nums) + 1:05d}" if nums else f"{prefix}00001"
    except Exception as e:
        print(f"ID Error: {e}"); return f"{prefix}99999"

def search_device(query_value):
    all_items = inventory_sheet.get_all_records()
    all_faults = fault_sheet.get_all_records()
    results = []
    query_lower = str(query_value).lower().strip()

    for item in all_items:
        bid = str(item.get('Blume ID', ''))
        item_faults = [f for f in all_faults if str(f.get('Blume ID')) == bid]
        formatted_faults = [{"Ticket ID": f.get('Ticket ID', 'N/A'), "Issue Date": f.get('Issue Date', 'N/A'),
                             "Status": f.get('Device Status', 'N/A'), "Notes": f.get('Issue Notes', '')} for f in item_faults]

        if query_lower == bid.lower() or any(query_lower in str(f["Status"]).lower() for f in formatted_faults):
            results.append({
                "Blume ID": bid,
                "Item Category": item.get('Item Category', 'Unknown'),
                "Serial Number": item.get('Serial Number', 'N/A'),
                "Originated Date": item.get('Originated Date', 'N/A'),
                "Last Service": item.get('Last Service', 'N/A'),
                "issues": formatted_faults 
            })
    return results

def get_device_history(blume_id):
    history = []
    inv = inventory_sheet.get_all_records()
    for item in inv:
        if str(item.get('Blume ID')) == str(blume_id):
            history.append({"date": item.get('Originated Date', '2000-01-01'), "event": "Device Created", 
                            "type": "ORIGIN", "notes": f"Serial: {item.get('Serial Number')}", "color": "#3498DB"})
    
    faults = fault_sheet.get_all_records()
    for f in faults:
        if str(f.get('Blume ID')) == str(blume_id):
            history.append({"date": f.get('Issue Date'), "event": f"FAULT: {f.get('Device Status')}", 
                            "type": "ACTIVE", "notes": f.get('Issue Notes'), "color": "#E74C3C"})

    resolved = repair_sheet.get_all_records()
    for r in resolved:
        if str(r.get('Blume ID')) == str(blume_id):
            history.append({"date": r.get('Resolved Date'), "event": "REPAIR COMPLETE", 
                            "type": "RESOLVED", "notes": r.get('Tech Notes'), "color": "#27AE60"})

    history.sort(key=lambda x: x['date'], reverse=True)
    return history
def get_fleet_stats():
    """Calculates counts for the Dashboard Pulse."""
    try:
        # 1. Get all Inventory (Sheet 1) and Active Faults (Sheet 2)
        all_inventory = inventory_sheet.get_all_records()
        all_active_faults = fault_sheet.get_all_records()
        
        # 2. Count Active Faults (The RED Pulse)
        broken_count = len(all_active_faults)
        
        # Create a set of IDs that are currently broken to avoid double-counting
        broken_ids = {str(f.get('Blume ID')) for f in all_active_faults}
        
        overdue_count = 0
        healthy_count = 0
        today = datetime.now()

        for item in all_inventory:
            bid = str(item.get('Blume ID'))
            
            # Skip if it's already in the 'Broken' bucket
            if bid in broken_ids:
                continue
                
            # 3. Check Maintenance (The YELLOW Pulse)
            # Pull from Column E (Last Service)
            last_service_str = item.get('Last Service')
            
            try:
                last_date = datetime.strptime(last_service_str, "%Y-%m-%d")
                days_since = (today - last_date).days
                if days_since >= 180:
                    overdue_count += 1
                else:
                    # 4. If not broken and not overdue, it's HEALTHY (The GREEN Pulse)
                    healthy_count += 1
            except (ValueError, TypeError):
                # If date is missing/invalid, treat as overdue/needs attention
                overdue_count += 1

        return {
            "broken": broken_count,
            "overdue": overdue_count,
            "healthy": healthy_count
        }
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"broken": 0, "overdue": 0, "healthy": 0}