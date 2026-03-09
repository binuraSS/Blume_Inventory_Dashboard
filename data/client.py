import gspread
from google.oauth2.service_account import Credentials
import time

SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(creds)

SPREADSHEET_NAME = "test spreadsheet"
spreadsheet = client.open(SPREADSHEET_NAME)

# Centralized Worksheet Objects
inventory_sheet = spreadsheet.get_worksheet(0)
fault_sheet = spreadsheet.get_worksheet(1)
repair_sheet = spreadsheet.get_worksheet(2)

def safe_get_records(worksheet):
    """Retries connection if Google drops it (Fixes 'Connection aborted')."""
    for attempt in range(3):
        try:
            return worksheet.get_all_records()
        except Exception as e:
            print(f"Connection attempt {attempt+1} failed: {e}")
            time.sleep(1.5)
    return []