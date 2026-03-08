import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime
import time

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

from datetime import datetime

def get_maintenance_status(blume_id, inventory_data, archive_data):
    """Uses provided data lists to check maintenance without calling the API again."""
    device_info = next((item for item in inventory_data if str(item.get('Blume ID')) == str(blume_id)), None)
    
    if not device_info:
        return "Unknown", 0, False

    last_date_str = device_info.get('Originated Date', '2000-01-01')
    
    # Filter the archive data we already fetched
    device_history = [r for r in archive_data if str(r.get('Blume ID')) == str(blume_id)]
    
    if device_history:
        device_history.sort(key=lambda x: x.get('Resolved Date', '2000-01-01'), reverse=True)
        last_date_str = device_history[0]['Resolved Date']

    try:
        last_seen = datetime.strptime(last_date_str, "%Y-%m-%d")
        days_since = (datetime.today() - last_seen).days
        return last_date_str, days_since, (days_since > 180)
    except:
        return "Invalid", 0, False

# --- CORE FUNCTIONS (RESTORED & UPDATED) ---

def add_device(blume_id, item, serial, date):
    """Adds new device to Sheet 1. Also sets the initial 'Last Service' to the creation date."""
    # Row: Blume ID, Item, Serial, Originated Date, Last Service (Sync Column)
    inventory_sheet.append_row([blume_id, item, serial, date, date])

def report_fault(blume_id, status, notes):
    """Logs the fault to Sheet 2 with 'PENDING' in the Progress Level column."""
    try:
        new_tid = get_next_ticket_id()
        issue_date = datetime.today().strftime("%Y-%m-%d")
        # Column 6 is now explicitly 'PENDING'
        new_row = [new_tid, blume_id, issue_date, status, notes, "PENDING"]
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
    # Use our new safe fetcher to avoid 'Connection Aborted'
    all_items = safe_get_records(inventory_sheet)
    all_faults = safe_get_records(fault_sheet)
    
    results = []
    query_lower = str(query_value).lower().strip()

    for item in all_items:
        bid = str(item.get('Blume ID', ''))
        # Filter faults for this specific device
        item_faults = [f for f in all_faults if str(f.get('Blume ID')) == bid]
        
        formatted_faults = [{
            "Ticket ID": f.get('Ticket ID', 'N/A'),
            "Status": f.get('Device Status', 'N/A'),
            "Notes": f.get('Issue Notes', ''),
            "Progress Level": f.get('Progress Level', 'PENDING') # Match new Column 6
        } for f in item_faults]

        # Search by ID or Status
        if query_lower == "" or query_lower in bid.lower() or any(query_lower in str(f["Status"]).lower() for f in formatted_faults):
            results.append({
                "Blume ID": bid,
                "Item Category": item.get('Item Category', 'Unknown'),
                "Serial Number": item.get('Serial Number', 'N/A'),
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
    """Calculates the 🟢🟡🔴 counts for the Pulse Cards."""
    try:
        inventory = inventory_sheet.get_all_records()
        active_faults = fault_sheet.get_all_records()
        
        broken_count = len(active_faults)
        broken_ids = {str(f.get('Blume ID')) for f in active_faults}
        
        overdue_count = 0
        healthy_count = 0
        today = datetime.now()

        for item in inventory:
            bid = str(item.get('Blume ID'))
            if bid in broken_ids: continue # Already counted in Red
            
            # Use Column E (Last Service)
            last_service_str = item.get('Last Service', '')
            try:
                last_date = datetime.strptime(last_service_str, "%Y-%m-%d")
                if (today - last_date).days >= 180:
                    overdue_count += 1
                else:
                    healthy_count += 1
            except:
                overdue_count += 1 # Default to overdue if date is missing

        return {"broken": broken_count, "overdue": overdue_count, "healthy": healthy_count}
    except Exception as e:
        print(f"Stats Error: {e}")
        return {"broken": 0, "overdue": 0, "healthy": 0}

def get_recent_activity(limit=8):
    """Combines Sheet 2 and Sheet 3 for the Live Feed."""
    try:
        # Get last few from Active and last few from Archive
        active_raw = fault_sheet.get_all_records()[-limit:]
        repair_raw = repair_sheet.get_all_records()[-limit:]
        
        feed = []
        # Items from Repair Sheet (Sheet 3) - Green
        for r in repair_raw:
            feed.append({
                "bid": r.get("Blume ID", "N/A"),
                "event": "Fixed & Archived",
                "color": "#1E8E3E" # Green
            })
        # Items from Fault Sheet (Sheet 2) - Red
        for f in active_raw:
            feed.append({
                "bid": f.get("Blume ID", "N/A"),
                "event": "Fault Reported",
                "color": "#D93025" # Red
            })
        
        feed.reverse() # Newest on top
        return feed[:limit]
    except:
        return []
    
def update_ticket_status(ticket_id, new_status):
    """Updates 'Progress Level' (Column 6)."""
    try:
        records = fault_sheet.get_all_records()
        for i, row in enumerate(records):
            if str(row.get('Ticket ID')) == str(ticket_id):
                # Update Column 6 (Progress Level)
                fault_sheet.update_cell(i + 2, 6, new_status) 
                time.sleep(1) # Quota safety
                return True
        return False
    except Exception as e:
        print(f"Update Error: {e}")
        return False
    
def archive_resolved_ticket(ticket_id, tech_notes):
    """Moves ticket to Sheet 4 and cleans up Sheet 2."""
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
        # Structure for Sheet 4: Ticket ID, Blume ID, Date, Status, Notes, Progress, Tech Notes, Resolved Date
        new_row = [
            target_row[0], target_row[1], target_row[2], 
            target_row[3], target_row[4], "RESOLVED",    
            tech_notes, resolved_date  
        ]

        repair_sheet.append_row(new_row)
        fault_sheet.delete_rows(row_index)
        update_last_service(target_row[1]) 
        return True
    except Exception as e:
        print(f"Archive Error: {e}")
        return False
    
def get_system_insights():
    """Calculates breakdown by Category by searching for the correct column."""
    try:
        active_faults = fault_sheet.get_all_records()
        if not active_faults:
            return []
            
        # Get the first row to see what the headers actually are
        sample_row = active_faults[0]
        
        # Try to find the category column among common naming conventions
        possible_keys = ["Item Category", "Category", "Device Type", "Type", "Device Status"]
        target_key = next((k for k in possible_keys if k in sample_row), None)
        
        stats = {}
        for f in active_faults:
            # If we found a valid key, use it. Otherwise, use 'Unknown Column'
            val = f.get(target_key, "Uncategorized") if target_key else "Uncategorized"
            stats[val] = stats.get(val, 0) + 1
            
        return sorted(stats.items(), key=lambda x: x[1], reverse=True)
    except Exception as e:
        print(f"Detailed Insights Error: {e}")
        return []
    
def safe_get_records(worksheet):
    """Attempt to fetch records with a retry if Google drops the connection."""
    for attempt in range(3):
        try:
            return worksheet.get_all_records()
        except Exception as e:
            print(f"Connection attempt {attempt+1} failed: {e}")
            time.sleep(2) # Wait 2 seconds before trying again
    return []