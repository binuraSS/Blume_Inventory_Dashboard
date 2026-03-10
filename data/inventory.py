from datetime import datetime
from .client import inventory_sheet, fault_sheet, repair_sheet, safe_get_records
from styles import G_RED, G_BLUE, G_BORDER, G_SUBTEXT # Add any other colors you used

def add_device(blume_id, item, serial, date):
    """Adds new device to Sheet 1."""
    inventory_sheet.append_row([blume_id, item, serial, date, date])

def update_last_service(blume_id):
    """Updates the 'Last Service' column (Col 5) in Sheet 1."""
    try:
        cell = inventory_sheet.find(str(blume_id))
        if cell:
            today = datetime.today().strftime("%Y-%m-%d")
            inventory_sheet.update_cell(cell.row, 5, today)
            return True
    except Exception as e:
        print(f"Sync Error: {e}")
        return False

def get_maintenance_status(blume_id, inventory_data, archive_data = None):
    device_info = next((item for item in inventory_data if str(item.get('Blume ID')) == str(blume_id)), None)
    if not device_info: return "Unknown", 0, False

    last_date_str = device_info.get('Last Service') or device_info.get('Originated Date', '2000-01-01')
    
    try:
        last_seen = datetime.strptime(str(last_date_str).strip(), "%Y-%m-%d")
        days_since = (datetime.today() - last_seen).days
        # CHANGE THIS TO 90
        return last_date_str, days_since, (days_since >= 90)
    except:
        return "Invalid", 0, True # If date is broken, it's overdue
    

def get_maintenance_list():
    inventory = safe_get_records(inventory_sheet)
    active_faults = safe_get_records(fault_sheet)
    
    broken_ids = {str(f.get('Blume ID')) for f in active_faults}
    processed_list = []
    
    # Standardize 'today' to the start of the day for clean math
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    MAINTENANCE_LIMIT = 30 

    for item in inventory:
        bid = str(item.get('Blume ID')).strip()
        if not bid or bid == "None": continue 
        
        last_service = item.get('Last Service')
        originated = item.get('Originated Date')
        
        # Priority: Last Service -> Originated Date -> None
        date_str = last_service if last_service else originated
        
        # Default safety state: If date is missing, it's overdue
        days_remaining = -999 
        status = "Overdue (No Date)"
        color = G_RED

        if date_str:
            try:
                # Strip and parse the date string
                last_date = datetime.strptime(str(date_str).strip(), "%Y-%m-%d")
                days_since = (today - last_date).days
                days_remaining = MAINTENANCE_LIMIT - days_since
                
                if bid in broken_ids:
                    status = "Under Repair"
                    color = "#602505" 
                elif days_remaining <= 0:
                    status = "Overdue"
                    color = G_RED
                elif days_remaining <= 7:
                    status = "Due Soon"
                    color = "#D97706" 
                else:
                    status = "Healthy"
                    color = "#059669"
            except Exception:
                status = "Overdue (Fix Date)"
                color = G_RED
        
        processed_list.append({
            "bid": bid,
            "category": item.get('Item Category', 'Unknown'),
            "last_service": date_str if date_str else "Missing",
            "days_remaining": days_remaining,
            "status": status,
            "color": color
        })
            
    # Sort: Lowest days_remaining (most overdue) at the top
    return sorted(processed_list, key=lambda x: x['days_remaining'])          


def search_device(query_value):
    all_items = safe_get_records(inventory_sheet)
    all_faults = safe_get_records(fault_sheet)
    results = []
    query_lower = str(query_value).lower().strip()

    for item in all_items:
        bid = str(item.get('Blume ID', ''))
        item_faults = [f for f in all_faults if str(f.get('Blume ID')) == bid]
        formatted_faults = [{
            "Ticket ID": f.get('Ticket ID', 'N/A'),
            "Status": f.get('Device Status', 'N/A'),
            "Notes": f.get('Issue Notes', ''),
            "Progress Level": f.get('Progress Level', 'PENDING')
        } for f in item_faults]

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
    
    inv = safe_get_records(inventory_sheet)
    active_faults = safe_get_records(fault_sheet)
    resolved_repairs = safe_get_records(repair_sheet)
    
    # 1. Device Registration
    for item in inv:
        if str(item.get('Blume ID')) == str(blume_id):
            history.append({
                "date": item.get('Originated Date'), 
                "event": "Device Registered", 
                "details": f"Initial Setup - SN: {item.get('Serial Number')}",
                "color": "#3498DB"
            })
    
    # 2. Active Faults (Current reported errors)
    for f in active_faults:
        if str(f.get('Blume ID')) == str(blume_id):
            history.append({
                "date": f.get('Issue Date'), 
                "event": f"Active Fault: {f.get('Device Status')}", 
                "details": f"Reported Error: {f.get('Issue Notes')}",
                "color": "#E74C3C" 
            })
    
    # 3. Resolved Repairs (The "Full Picture")
    for r in resolved_repairs:
        if str(r.get('Blume ID')) == str(blume_id):
            # We combine the Reported Error + The Tech Fix
            reported_as = r.get('Status', 'Unknown Issue')
            fix_notes = r.get('Tech Notes', 'No notes provided')
            
            history.append({
                "date": r.get('Resolved Date'), 
                "event": "Repair Complete", 
                "details": f"Reported Error: {reported_as}\n      Tech Fix: {fix_notes}",
                "color": "#27AE60" 
            })
    
    history.sort(key=lambda x: x['date'] if x['date'] else "", reverse=True)
    return history

def mark_as_inspected(blume_id):
    return update_last_service(blume_id)
