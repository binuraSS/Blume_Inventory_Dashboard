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
    
def calculate_mttr():
    try:
        repairs = safe_get_records(repair_sheet)
        if not repairs: return 0
        
        total_days = 0
        completed_repairs = 0
        
        for r in repairs:
            start_str = r.get('Date Logged')
            end_str = r.get('Date Resolved')
            
            if start_str and end_str:
                start = datetime.strptime(str(start_str).strip(), "%Y-%m-%d")
                end = datetime.strptime(str(end_str).strip(), "%Y-%m-%d")
                
                # Difference in days
                total_days += (end - start).days
                completed_repairs += 1
        
        return round(total_days / completed_repairs, 1) if completed_repairs > 0 else 0
    except:
        return 0
    
def get_recurring_issues():
    try:
        # Get all historical repairs
        repairs = safe_get_records(repair_sheet)
        
        # Extract only the Blume IDs
        all_failed_ids = [str(r.get('Blume ID')).strip() for r in repairs if r.get('Blume ID')]
        
        # Count occurrences
        counts = Counter(all_failed_ids)
        
        # Return only those that have failed 2 or more times
        # Format: [("BL-024", 3), ("BL-010", 2)]
        return [(bid, count) for bid, count in counts.most_common() if count >= 2]
    except:
        return []    
    
def get_reliability_metrics():
    try:
        open_faults = safe_get_records(fault_sheet)
        resolved_repairs = safe_get_records(repair_sheet)
        
        total_seconds = 0
        total_cases = 0
        all_ids = []
        now = datetime.now()

        combined_list = open_faults + resolved_repairs

        for entry in combined_list:
            # Normalize keys to handle spaces or casing
            clean_entry = {str(k).strip(): v for k, v in entry.items()}
            
            bid = str(clean_entry.get('Blume ID', '')).strip()
            if not bid or bid.lower() == "none": continue
            all_ids.append(bid)
            
            # Use YOUR actual headers: "Issue Date" and "Resolved Date"
            start_str = clean_entry.get('Issue Date')
            end_str = clean_entry.get('Resolved Date')
            
            if start_str:
                try:
                    # Parse the Issue Date
                    start_dt = datetime.strptime(str(start_str).strip(), "%Y-%m-%d")
                    
                    # Check if it's resolved or still active
                    if end_str and str(end_str).lower() != "none" and str(end_str).strip() != "":
                        end_dt = datetime.strptime(str(end_str).strip(), "%Y-%m-%d")
                        duration = end_dt - start_dt
                    else:
                        # Still an active fault
                        duration = now - start_dt
                    
                    total_seconds += duration.total_seconds()
                    total_cases += 1
                except Exception as e:
                    # This will catch if the date format in the sheet isn't YYYY-MM-DD
                    print(f"ID: {bid} | Date Error: {e}")
                    continue

        avg_days = (total_seconds / total_cases) / 86400 if total_cases > 0 else 0
        
        # Recurring Issues
        counts = Counter(all_ids)
        lemons = [{"bid": bid, "count": count} for bid, count in counts.most_common(3) if count >= 2]

        return {"mttr": round(avg_days, 1), "lemons": lemons}
    except Exception as e:
        print(f"Reliability Error: {e}")
        return {"mttr": 0, "lemons": []}