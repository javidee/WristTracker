import cv2    
import time
import numpy as np
import HandTrackingModule as htm
import ctypes
import math
import threading
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(detectionCon=0.8)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
vol_range=volume.GetVolumeRange()
volume.SetMasterVolumeLevel(0,None)
min_vol = -65
max_vol = 0
vol_bar= 0
first_iteration = True
vol = 0
vol_p = 0
lock = threading.Lock()
time_condition_met = None
length_2 = 45



def volume_save():
    global vol
    global vol_p
    while True:
        time.sleep(2)
        with lock:
            vol_p = vol
              
    
def volume_changing(img, lmList):
    
    global first_iteration
    global vol
    global vol_p
    global time_condition_met
    global length_2
    if len(lmList) != 0  :
        
        #print(lmList[4],lmList[8])
        x1, y1 = lmList[4][1] , lmList[4][2]
        x2, y2 = lmList[8][1] , lmList[8][2]
        x3, y3 = lmList[5][1] , lmList[5][2]
        x4, y4 = lmList[9][1] , lmList[9][2]
        length_p = math.hypot(x4-x3,y4-y3)
        cx,cy = (x1+x2)//2, (y1+y2)//2
        if length_2 > length_p:
            k = length_p/length_2
        else :
            k = length_2/length_p
        #print(k)
        length = math.hypot(x2-x1,y2-y1)/k
        if length < 50 and first_iteration:
            cv2.circle(img, (x1,y1), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (x2,y2), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (cx,cy), 5, (255,0,255), cv2.FILLED )
            cv2.line(img, (x1,y1),(x2,y2),(0,165,255),3)
            #print(length)

            # Hand Range 50 - 300
            # volume range -65 - 0

            vol = np.interp(length,[50,300],[min_vol, max_vol])
            vol_bar = np.interp(length,[50,300],[475,155])
            #print(int(length),vol)
            volume.SetMasterVolumeLevel(vol, None)
            cv2.rectangle(img, (0,150), (40, 480), (250, 250, 250), 5 )
            cv2.rectangle(img, (5,int(vol_bar)), (35,475), (250, 0, 250), cv2.FILLED )
            if vol==-65:
                cv2.circle(img, (cx,cy), 5, (0,255,0), cv2.FILLED )
            if vol==0:
                cv2.circle(img, (x1,y1), 10, (0,0,255), cv2.FILLED )
                cv2.circle(img, (x2,y2), 10, (0,0,255), cv2.FILLED )
            first_iteration = False    
            
            return vol , first_iteration 
        
        if  first_iteration != True :
            x1, y1 = lmList[4][1] , lmList[4][2]
            x2, y2 = lmList[8][1] , lmList[8][2]
            cx,cy = (x1+x2)//2, (y1+y2)//2
            length =math.hypot(x2-x1,y2-y1)/k
            #print(length)
            cv2.circle(img, (x1,y1), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (x2,y2), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (cx,cy), 5, (255,0,255), cv2.FILLED )
            cv2.line(img, (x1,y1),(x2,y2),(0,165,255),3)
            #print(length)

            # Hand Range 50 - 300
            # volume range -65 - 0

            vol = np.interp(length,[50,300],[min_vol, max_vol])
            vol_bar = np.interp(length,[50,300],[475,155])
            #print(int(length),vol)
            volume.SetMasterVolumeLevel(vol, None)
            cv2.rectangle(img, (0,150), (40, 480), (250, 250, 250), 5 )
            cv2.rectangle(img, (5,int(vol_bar)), (35,475), (250, 0, 250), cv2.FILLED )
            if vol==-65:
                cv2.circle(img, (cx,cy), 5, (0,255,0), cv2.FILLED )
            if vol==0:
                cv2.circle(img, (x1,y1), 10, (0,0,255), cv2.FILLED )
                cv2.circle(img, (x2,y2), 10, (0,0,255), cv2.FILLED )
            if  abs(vol - vol_p) < 10 :
                if time_condition_met is None:
                    time_condition_met = time.time()
                # перевіряє чи виконується умова 2 сек
                elif time.time() - time_condition_met >= 2:
                    first_iteration = True
                    time_condition_met = None  # збиває таймер
            else:
                # якщо умова не виконана збиває таймер
                time_condition_met = None 
            return vol
        
           

  
volume_save_thread = threading.Thread(target=volume_save, daemon=True)
volume_save_thread.start()      
    
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    #fps_img = detector.Fps_m(img)
    lmList = detector.findPosition(img)
    
    volume_c=volume_changing(img, lmList)
    #print(vol_p)
    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty("img", cv2.WND_PROP_VISIBLE)<1:
        break
    cv2.waitKey(1) 



    


