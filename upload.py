import gspread
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
# import socket # Optional, for socket.timeout

# --- Configuration Constants ---
DEFAULT_KEY_FILE = 'Auth/Cred.json'
DEFAULT_SPREADSHEET_ID = '1AKZrGn62J9rD6MSiKPEDUj2GF-k0ThigakGzP-xcafc'

class GoogleSheet():
    def __init__(self):
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        # Key = 'Auth/Cred.json' # Replaced by constant
        # self.SpreadsheetId = '1AKZrGn62J9rD6MSiKPEDUj2GF-k0ThigakGzP-xcafc' # Replaced by constant
        self.SpreadsheetId = DEFAULT_SPREADSHEET_ID
        creds = None
        try:
            creds = service_account.Credentials.from_service_account_file(DEFAULT_KEY_FILE, scopes=scope)
            service = build('sheets', 'v4', credentials=creds)
            self.sheet = service.spreadsheets()
        except Exception as e:
            print(f"Failed to initialize GoogleSheet service: {e}")
            self.sheet = None # Ensure sheet is None if init fails

        self.Entry = 0
        self.Exit = 0

    def ReadData(self):
        if not self.sheet:
            print("GoogleSheet service not initialized. Skipping ReadData.")
            self.Entry = 0
            self.Exit = 0
            return
        try:
            result = self.sheet.values().get(spreadsheetId=self.SpreadsheetId,range="A:C").execute()
            values = result.get('values', [])
            self.Entry = len([x for x in values if 'Entry' in x])
            self.Exit = len([x for x in values if 'Exit' in x])
        except HttpError as e:
            print(f"Google Sheets API Error during ReadData: {e}")
            self.Entry = 0 
            self.Exit = 0
        except Exception as e: 
            print(f"An unexpected error occurred during ReadData: {e}")
            self.Entry = 0
            self.Exit = 0
     
    def sendData(self, Fecha,Registo, Hora):
        if not self.sheet:
            print("GoogleSheet service not initialized. Skipping sendData.")
            return
        data = [[Fecha, Registo, Hora]]
        try:
            result = self.sheet.values().append(spreadsheetId = self.SpreadsheetId,
                                                range='A1',
                                                valueInputOption='USER_ENTERED',
                                                body={'values': data}).execute()
            # print(f"Data sent to Google Sheet: {result}") # Optional: for debugging
        except HttpError as e:
            print(f"Google Sheets API Error during sendData: {e}")
        except Exception as e: 
            print(f"An unexpected error occurred during sendData: {e}")