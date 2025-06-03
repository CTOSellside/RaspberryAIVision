import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import exceptions as firebase_exceptions
from threading import Thread
from datetime import datetime
import time

# --- Configuration Constants ---
DEFAULT_FIREBASE_CRED_PATH = "Auth/credFire.json"
DEFAULT_FIREBASE_DB_URL = 'https://coffeemondo-365813-default-rtdb.firebaseio.com/'

class FireData(Thread):
    def __init__(self):
        Thread.__init__(self)
        cred = credentials.Certificate(DEFAULT_FIREBASE_CRED_PATH)

        firebase_admin.initialize_app(cred, {
        'databaseURL': DEFAULT_FIREBASE_DB_URL
        })
        self.Stream = False
        self.x_offset = 0
        self.y_offset = 0
        self.cantZoom = 0
        self.status = True
        self.Hora = datetime.strptime('23:59:59', "%X").time()
        
    def run(self):
        while self.status:
            try:
                data = db.reference('live').get()
                if data is None: # Check if data is None (e.g. path doesn't exist)
                    print("Firebase: 'live' path returned None. Check path or permissions.")
                    time.sleep(1) # Sleep longer if path is problematic
                    continue

                self.Stream = data.get('Streaming', self.Stream) # Use .get for safer access
                
                zoom_input = data.get('zoomInput')
                if zoom_input: # Check if zoomInput exists
                    self.x_offset = zoom_input.get('inputLR', self.x_offset)
                    self.y_offset = zoom_input.get('inputTB', self.y_offset)
                    self.cantZoom = zoom_input.get('zoom', self.cantZoom)
                
                hora_str = data.get('Hora')
                if hora_str: # Check if Hora exists
                    self.Hora = datetime.strptime(hora_str, "%X").time()

            except KeyError as e:
                print(f"Firebase: Key not found in live data: {e}")
            except firebase_exceptions.FirebaseError as e:
                print(f"Firebase: An error occurred with Firebase operations: {e}")
            except ValueError as e: # For strptime issues
                print(f"Firebase: Error parsing 'Hora' value: {e}")
            except Exception as e:
                print(f"Firebase: An unexpected error occurred: {e}")
            
            time.sleep(0.1) # Poll every 100ms
                
    def stop(self):
        self.status = False