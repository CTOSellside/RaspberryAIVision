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

counter, fps = 0, 0
fps_avg_frame_count = 10
start_time = time.time()

width = 640#int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = 410#int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#Camera 1
cap1 = cv2.VideoCapture(0)#("rtsp://192.168.4.16:8554/mjpeg/1")
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
proc = False
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
    '-b:v', '500k',  # Establecer la tasa de bits de video correctamente aquí
    '-g', '30',
    '-pix_fmt', 'yuv420p',
    '-f', 'flv',
    'rtmp://visionsinc.xyz/show/stream'
]

proc = sp.Popen(cmd, stdin = sp.PIPE)
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
        if not ret1:
            print('Camara 1 no iniciada')
        #if not ret2:
            #print('Camara 2 no iniciada')
        #if not ret3:
            #print('Camara 3 no iniciada')
        #break
    
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
        try:
            if not stream_log:
                print("Stream On")
            proc.stdin.write(frame1.tobytes())
            stream_log = True
        except Exception as e:
            proc = sp.Popen(cmd, stdin = sp.PIPE)
    else:
        if stream_log == True:
            proc.terminate()
            print('Stream Off')
            stream_log = False
    time.sleep(1/1000)
            
if proc is not False:
    proc.terminate()
cap1.release()
#cap2.release()
#cap3.release()
cv2.destroyAllWindows()
FireData.stop()



