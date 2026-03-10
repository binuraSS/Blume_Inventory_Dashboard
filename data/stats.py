from datetime import datetime
from .client import inventory_sheet, fault_sheet, repair_sheet, safe_get_records
from collections import Counter

from datetime import datetime
from .client import inventory_sheet, fault_sheet, safe_get_records

def get_fleet_stats():
    try:
        inventory = safe_get_records(inventory_sheet)
        active_faults = safe_get_records(fault_sheet)

        broken_ids = {str(f.get('Blume ID')).strip() for f in active_faults}

        overdue_count = 0
        healthy_count = 0

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        MAINTENANCE_LIMIT = 30

        for item in inventory:
            clean_item = {str(k).strip().lower(): v for k, v in item.items()}
            bid = str(clean_item.get('blume id', '')).strip()

            if not bid or bid.lower() == "none" or bid in broken_ids:
                continue

            date_str = clean_item.get('last service') or clean_item.get('originated date')
            print(f"DEVICE {bid} | DATE FOUND: {date_str}")

            if not date_str or str(date_str).strip().lower() == "none":
                overdue_count += 1
                continue

            try:
                date_val = str(date_str).strip().replace("/", "-").split(" ")[0]
                last_date = datetime.strptime(date_val, "%Y-%m-%d")
                days_since = (today - last_date).days

                if days_since >= MAINTENANCE_LIMIT:
                    overdue_count += 1
                else:
                    healthy_count += 1
            except:
                overdue_count += 1

        return {
            "broken": len(broken_ids),
            "overdue": overdue_count,
            "healthy": healthy_count
        }

    except Exception as e:
        print(f"Stats Calculation Error: {e}")
        return {"broken": 0, "overdue": 0, "healthy": 0}
        

def get_system_insights():
    """Returns a list of (Issue Type, Count) for the visual bars."""
    try:
        faults = safe_get_records(fault_sheet)
        
        # We look at the 'Device Status' column from the Fault Sheet 
        # (This contains the "Physical Damage", "Tracking Error", etc.)
        issues = [str(f.get('Device Status', 'Unknown Issue')) for f in faults]
        
        # This returns the counts of specific issues
        return Counter(issues).most_common(5)
    except Exception as e:
        print(f"Insights Error: {e}")
        return []
    
def get_recent_activity():
    """Combines latest faults and repairs for the live feed."""
    try:
        faults = safe_get_records(fault_sheet)[-3:]
        repairs = safe_get_records(repair_sheet)[-3:]
        
        activity = []
        for f in faults:
            activity.append({"bid": f.get('Blume ID'), "event": "New Fault Logged", "color": "#E74C3C"})
        for r in repairs:
            activity.append({"bid": r.get('Blume ID'), "event": "Repair Resolved", "color": "#27AE60"})
            
        return activity
    except:
        return []