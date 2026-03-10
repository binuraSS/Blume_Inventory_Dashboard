import os
import sys
import gspread
from google.oauth2.service_account import Credentials
import time

# --- 1. Resource Path Helper ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 2. Authentication Setup ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
CRED_FILE = resource_path("credentials.json")

def get_gspread_client():
    """Returns an authorized gspread client."""
    try:
        creds = Credentials.from_service_account_file(CRED_FILE, scopes=SCOPES)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Authentication Error: {e}")
        return None

# Initial Connection
client = get_gspread_client()
SPREADSHEET_NAME = "test spreadsheet"

try:
    spreadsheet = client.open(SPREADSHEET_NAME)
    # Centralized Worksheet Objects
    inventory_sheet = spreadsheet.get_worksheet(0)
    fault_sheet = spreadsheet.get_worksheet(1)
    repair_sheet = spreadsheet.get_worksheet(2)
except Exception as e:
    print(f"Critical Error: Could not open spreadsheet. {e}")

# --- 3. Robust Data Fetching ---
def safe_get_records(worksheet):
    """
    Retries connection if Google drops it or if credentials expire.
    This is the engine that keeps your app from crashing during long sessions.
    """
    global client, spreadsheet, inventory_sheet, fault_sheet, repair_sheet
    
    for attempt in range(3):
        try:
            return worksheet.get_all_records()
        except Exception as e:
            print(f"Connection attempt {attempt+1} failed: {e}")
            
            # If it's a 401/Expired error, let's re-authorize
            if "expired" in str(e).lower() or "401" in str(e):
                print("Re-authorizing Google Client...")
                client = get_gspread_client()
                spreadsheet = client.open(SPREADSHEET_NAME)
                # Re-map the worksheets to the new client session
                inventory_sheet = spreadsheet.get_worksheet(0)
                fault_sheet = spreadsheet.get_worksheet(1)
                repair_sheet = spreadsheet.get_worksheet(2)
            
            time.sleep(1.5)
            
    return []