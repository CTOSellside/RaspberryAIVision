import argparse
import sys
import time
import subprocess as sp
import threading

import cv2
import numpy as np
import math
from datetime import datetime
from upload import GoogleSheet
from functions import *
from dataFirebase import FireData

# --- Configuration Constants ---
CAMERA_SOURCE_1 = 0 # Or "rtsp://192.168.4.16:8554/mjpeg/1"
# CAMERA_SOURCE_2 = "rtsp://192.168.4.11:8554/mjpeg/1" # Example if used
# CAMERA_SOURCE_3 = "rtsp://192.168.4.7:8554/mjpeg/1" # Example if used
FFMPEG_RTMP_URL = 'rtmp://visionsinc.xyz/show/stream'
# Note: Firebase related paths will be handled in dataFirebase.py adjustments

# --- Global Variables ---
counter, fps = 0, 0
fps_avg_frame_count = 10
start_time = time.time()

# --- Initialization ---
width = 640#int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) # Consider making these constants if not dynamically determined
height = 410#int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#Camera 1
cap1 = cv2.VideoCapture(CAMERA_SOURCE_1)#("rtsp://192.168.4.16:8554/mjpeg/1")
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

#Camera 2
#cap2 = cv2.VideoCapture("rtsp://192.168.4.11:8554/mjpeg/1")
#cap2.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#cap2.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

#Camera 3
#cap3 = cv2.VideoCapture("rtsp://192.168.4.7:8554/mjpeg/1")
#cap3.set(cv2.CAP_PROP_FRAME_WIDTH, width)
#cap3.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

centerPointsPrevFrame = []
trackingObjects = {}
trackId = 0

# ROI: Entry/Exit is determined by crossing this single line (0.5*width).
# Direction of movement across this line would distinguish entry/exit if full detection logic were active here.
roi_position_entry = 0.5 #rigth
roi_position_exit = 0.5 #left

position = [0,0,0,0] #left, right, up, down;
trackableobject = {}
Eje = True # x = True, y = False

#sheet = GoogleSheet()
#sheet.ReadData()
#### ZOOM
scale = 50
x_offset = 0
y_offset = 0
cantZoom = 0

## ENCENDER STREAM
StreamOn = True
stream_log = False
# proc = False # Initialize proc to None for clearer checks
proc = None 
try_counted = 0
cmd = [
    'ffmpeg',
    '-f', 'rawvideo',
    '-framerate', '30',
    '-s', '{}x{}'.format(width, height),
    '-pix_fmt', 'bgr24',
    '-i', '-',
    '-c:v', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    # TODO: Verify and adjust video bitrate ('500k' currently) for optimal stream quality and bandwidth usage.
    '-b:v', '500k',
    '-g', '30',
    '-pix_fmt', 'yuv420p',
    '-f', 'flv',
    FFMPEG_RTMP_URL
]

try:
    print("Initializing ffmpeg process...")
    proc = sp.Popen(cmd, stdin=sp.PIPE)
except Exception as e:
    print(f"Failed to start initial ffmpeg process: {e}")
    proc = None # Ensure proc is None if initial Popen fails

## RESET VALUE STREAMING
FireData = FireData()
FireData.start()

pxl_entr = [470,560]
#start_point = time.start();

center = (width // 2, height // 2)
radius = 20
colors = [(0, 255, 0), (0,0,255)]
start_time = time.time()
time_color = time.time()
color = 0
while True:
    
    # Simple trackId reset. In scenarios with many persistent objects or very long runs,
    # this could lead to track ID collisions. (Note: Full tracking logic not active in this script).
    if trackId > 100:
        trackId = 0
        trackableobject = {}
    
    #StreamOn = FireData.Stream
    cantZoom = FireData.cantZoom
    x_offset = FireData.x_offset
    y_offset = FireData.y_offset
    Hora_Alerta = FireData.Hora  ## 10:30:00
    Hora_Actual = datetime.now().time()
    
    ret1, frame1 = cap1.read()
    #ret2, frame2 = cap2.read()
    #ret3, frame3 = cap3.read()
    
    #cv2.imshow('frame_original', frame)
    
    key = cv2.waitKey(1)
    
    if not ret1: #or not ret2 or not ret3:
        #if not ret1: # This inner check is redundant if we break
        print("Error: Could not read frame from Camera 1 in StreamHLS.py. Exiting.")
        #if not ret2:
            #print('Camara 2 no iniciada')
        #if not ret3:
            #print('Camara 3 no iniciada')
        break # Exit the loop if frame reading fails
    
    counter +=1
    objects = []
    centerPointsCurFrame = []
    
    #frame = cv2.flip(frame, 1)
    #frame = cv2.flip(frame, 0)

    frame1 = cv2.resize(frame1, (width,height))
    #frame2 = cv2.resize(frame2, (width,height))
    #frame3 = cv2.resize(frame3, (width,height))         
    
    rgb_image1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2BGR)
    #rgb_image2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2BGR)
    #rgb_image3 = cv2.cvtColor(frame3, cv2.COLOR_RGB2BGR)
        
    fps_text = 'FPS = {:.1f}'.format(fps)

    cv2.putText(frame1, fps_text, (24,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1)
    #cv2.putText(frame2, fps_text, (24,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1)
    #cv2.putText(frame3, fps_text, (24,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1)

    #cv2.line(frame, (pxl_entr[0],  int(roi_position_entry*height)), (pxl_entr[1], int(roi_position_entry*height)),(0xFF,0,0),2)

    cv2.line(frame1, (int(roi_position_entry*width), 0),(int(roi_position_entry*width), height), (0xFF,0,0),2)
    #cv2.line(frame2, (int(roi_position_entry*width), 0),(int(roi_position_entry*width), height), (0xFF,0,0),2)
    #cv2.line(frame3, (int(roi_position_entry*width), 0),(int(roi_position_entry*width), height), (0xFF,0,0),2)

    #cv2.line(frame, (int(roi_position_exit*width), 0),(int(roi_position_exit*width), height), (0, 0, 255), 5)
    #cv2.putText(frame, f'Entrada:{sheet.Entry}; Salida: {sheet.Exit}',(10,15), 1,1, (255, 255, 255), 2, cv2.FONT_HERSHEY_SIMPLEX )        
    
            
    if time.time() -start_time > 10:
        cv2.circle(frame1, center, radius, colors[color], -1)
        
    if time.time() - time_color > 20:
        if color == 0:
            color = 1
        else:
            color = 0
        time_color = time.time()
    
    if key == 27:
        break
        
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    
    cv2.imshow('frame 1', frame1)
    #cv2.imshow('frame 2', frame2)
    #cv2.imshow('frame 3', frame3)
    
    if StreamOn == True:
        if proc and proc.poll() is None: # Check if proc is alive
            try:
                if not stream_log:
                    print("Stream On")
                proc.stdin.write(frame1.tobytes())
                stream_log = True
            except Exception as e: # Typically BrokenPipeError if ffmpeg crashes
                print(f"Error writing to ffmpeg stdin: {e}. Restarting ffmpeg.")
                if proc and proc.poll() is None:
                    print("Terminating existing ffmpeg process before restart...")
                    proc.terminate()
                    try:
                        proc.wait(timeout=1) # Wait a bit for it to terminate
                    except sp.TimeoutExpired:
                        print("ffmpeg did not terminate in time, killing.")
                        proc.kill() # Force kill if it doesn't terminate
                print("Restarting ffmpeg process...")
                try:
                    proc = sp.Popen(cmd, stdin=sp.PIPE)
                    stream_log = False # Reset stream_log as we just restarted
                except Exception as popen_e:
                    print(f"Failed to restart ffmpeg process: {popen_e}")
                    proc = None # Set proc to None if restart fails
        elif not proc or proc.poll() is not None: # If proc is dead or None, try to restart
            print("ffmpeg process is not running. Attempting to start/restart.")
            try:
                proc = sp.Popen(cmd, stdin=sp.PIPE)
                stream_log = False
            except Exception as popen_e:
                print(f"Failed to start/restart ffmpeg process: {popen_e}")
                proc = None
    else: # StreamOn is False
        if stream_log == True:
            if proc and proc.poll() is None: # Check if proc is alive
                print('Stream Off - Terminating ffmpeg process...')
                proc.terminate()
                try:
                    proc.wait(timeout=1)
                except sp.TimeoutExpired:
                    print("ffmpeg did not terminate in time on Stream Off, killing.")
                    proc.kill()
            else:
                print('Stream Off - ffmpeg process already stopped or None.')
            stream_log = False
    time.sleep(1/1000) # Consider increasing this if CPU usage is high
            
if proc and proc.poll() is None: # Check if proc is not None and is alive
    print("Script ending - Terminating ffmpeg process...")
    proc.terminate()
    try:
        proc.wait(timeout=1)
    except sp.TimeoutExpired:
        print("ffmpeg did not terminate in time at script end, killing.")
        proc.kill()
cap1.release()
#cap2.release()
#cap3.release()
cv2.destroyAllWindows()
FireData.stop()



