import cv2
import time
from threading import Thread

# ... (other functions like maxZoom, ZoomKey, etc. will remain above) ...

def maxZoom(cantZoom):
    maxX = (((cantZoom * 5) * 2) * 3)
    maxY = ((cantZoom * 5) * 5)
    return maxX,-maxX, maxY, -maxY

def ZoomKey(cantZoom):
    scale = 50 - (5 * cantZoom)

    if scale <= 5:
        scale = 5
 
    elif scale >=50:
        scale = 50
    
    return(scale, cantZoom)

def StatusZoom(scale, cantZoom,x_offset,y_offset):
    if scale <= 5:
        scale = 5
    elif scale >= 50:
        scale = 50


    max_width_zoom, min_widt_zoom, max_height_zoom, min_height_zoom = maxZoom(cantZoom)

    if x_offset >  max_width_zoom:
        x_offset = max_width_zoom
    elif x_offset < min_widt_zoom:
        x_offset = min_widt_zoom

    if y_offset >=  max_height_zoom:
        y_offset = max_height_zoom
    elif y_offset <= min_height_zoom:
        y_offset = min_height_zoom
        
    return scale, cantZoom, x_offset,y_offset

def DisplayZoom(frame, scale, x_offset, y_offset, width, height):
    centerX,centerY=int(height/2),int(width/2)
    radiusX,radiusY= int(scale*height/100),int(scale*width/100)

    minX,maxX=centerX-radiusX+y_offset,centerX+radiusX+y_offset
    minY,maxY=centerY-radiusY+x_offset,centerY+radiusY+x_offset

    if minX < 0:
        minX = 0
    if minY < 0:
        minY = 0
    if maxX > height:
        maxX = height
    if maxY > width:
        maxY = width

    cropped = frame[minX:maxX, minY:maxY]
    resized_cropped = cv2.resize(cropped, (width, height))

    return resized_cropped

_alert_thread = None # Global variable to hold the thread instance

class SendAlert(Thread):
    def __init__(self):
        super().__init__() # Correct way to call Thread constructor
        self.status = True
        # self.time = 60 * 5 # This attribute is not used by run() or timer()
        
    def run(self):
        while self.status:
            self.timer()
            # It's important that time.sleep uses self.status for timely exit
            # For example, sleep in smaller chunks or check status more often if sleep is long
            for _ in range(300): # Sleep for 300 seconds (5 minutes) but check status every second
                if not self.status:
                    break
                time.sleep(1)

    def stop(self):
        print("Stopping alert thread...") # Add a print for feedback
        self.status = False
        
class sendAlertTime(SendAlert):
    def timer(self):
        print('send Alert: Timer event occurred!') # Make message more specific

def SendAlertStatus(Value):
    global _alert_thread
    if Value:
        if _alert_thread is None or not _alert_thread.is_alive():
            _alert_thread = sendAlertTime()
            _alert_thread.start()
            print("Alert thread started.")
        else:
            print("Alert thread already running.")
    else: # Value is False
        if _alert_thread is not None and _alert_thread.is_alive():
            print("Attempting to stop alert thread...")
            _alert_thread.stop()
            _alert_thread.join(timeout=2) # Wait for thread to finish
            if _alert_thread.is_alive():
                print("Alert thread did not stop in time.")
            else:
                print("Alert thread stopped.")
            _alert_thread = None # Clear the global var after stopping
        else:
            print("Alert thread not running or already stopped.")