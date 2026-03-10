import re
import time
from datetime import datetime
from .client import fault_sheet, repair_sheet, safe_get_records
from .inventory import update_last_service

def get_next_ticket_id():
    prefix = "ID-"
    try:
        active_ids = fault_sheet.col_values(1)[1:]   
        archive_ids = repair_sheet.col_values(1)[1:] 
        all_known_ids = active_ids + archive_ids
        
        if not all_known_ids: 
            return f"{prefix}00001"
            
        nums = []
        for tid in all_known_ids:
            found = re.findall(r'\d+', str(tid))
            if found:
                nums.append(int(found[0]))
        
        return f"{prefix}{max(nums) + 1:05d}" if nums else f"{prefix}00001"
    except Exception as e:
        print(f"Ticket ID Generation Error: {e}")
        return f"{prefix}99999"

def report_fault(blume_id, status, notes):
    """Logs a new fault to the Google Sheet."""
    new_tid = get_next_ticket_id()
    issue_date = datetime.today().strftime("%Y-%m-%d")
    # Row format: Ticket ID, Blume ID, Date, Status, Notes, Progress Level
    new_row = [new_tid, blume_id, issue_date, status, notes, "Pending"]
    fault_sheet.append_row(new_row)
    return new_tid

def archive_resolved_ticket(ticket_id, tech_notes):
    """Moves ticket from Active Faults to Archives and updates Master List service date."""
    try:
        rows = fault_sheet.get_all_values()
        for i, row in enumerate(rows):
            if row[0] == ticket_id:
                resolved_date = datetime.today().strftime("%Y-%m-%d")
                # Structure: ID, BlumeID, StartDate, Status, Notes, Progress, TechNotes, EndDate
                new_row = [row[0], row[1], row[2], row[3], row[4], "Resolved", tech_notes, resolved_date]
                
                repair_sheet.append_row(new_row)
                fault_sheet.delete_rows(i + 1)
                update_last_service(row[1]) 
                return True
        return False
    except Exception as e:
        print(f"Archive Error: {e}")
        return False
    
def update_ticket_status(ticket_id, new_status):
    """Moves a ticket status (e.g., from Pending to In Progress)."""
    try:
        records = safe_get_records(fault_sheet)
        for i, row in enumerate(records):
            if str(row.get('Ticket ID')) == str(ticket_id):
                # +2 matches the header offset
                fault_sheet.update_cell(i + 2, 6, new_status) 
                time.sleep(1) # API Quota safety
                return True
        return False
    except Exception as e:
        print(f"Update Error: {e}")
        return False