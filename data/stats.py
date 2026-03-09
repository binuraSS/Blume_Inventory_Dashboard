from datetime import datetime
from .client import inventory_sheet, fault_sheet, repair_sheet, safe_get_records
from collections import Counter

def get_fleet_stats():
    """Calculates the top-level numbers for Pulse cards."""
    try:
        inventory = safe_get_records(inventory_sheet)
        active_faults = safe_get_records(fault_sheet)
        
        broken_ids = {str(f.get('Blume ID')) for f in active_faults}
        overdue_count = 0
        healthy_count = 0
        today = datetime.now()

        for item in inventory:
            bid = str(item.get('Blume ID'))
            if bid in broken_ids: continue
            
            last_service_str = item.get('Last Service', '')
            try:
                last_date = datetime.strptime(last_service_str, "%Y-%m-%d")
                if (today - last_date).days >= 180:
                    overdue_count += 1
                else:
                    healthy_count += 1
            except:
                overdue_count += 1

        return {"broken": len(active_faults), "overdue": overdue_count, "healthy": healthy_count}
    except Exception as e:
        print(f"Stats Error: {e}")
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