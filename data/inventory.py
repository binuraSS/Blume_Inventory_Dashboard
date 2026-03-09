from datetime import datetime
from .client import inventory_sheet, fault_sheet, repair_sheet, safe_get_records

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

def get_maintenance_status(blume_id, inventory_data, archive_data):
    device_info = next((item for item in inventory_data if str(item.get('Blume ID')) == str(blume_id)), None)
    if not device_info: return "Unknown", 0, False

    last_date_str = device_info.get('Last Service') or device_info.get('Originated Date', '2000-01-01')
    
    try:
        last_seen = datetime.strptime(last_date_str, "%Y-%m-%d")
        days_since = (datetime.today() - last_seen).days
        return last_date_str, days_since, (days_since > 180)
    except:
        return "Invalid", 0, False

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
