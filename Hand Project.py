import cv2    
import time
import numpy as np
import HandTrackingModule as htm
import ctypes
import math
import threading
from pynput import keyboard, mouse
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
first_iteration_volume = True
first_iteration_scroll = True
Scroll_on = False
Volume_on = False
vol = 0
vol_p = 0
lock = threading.Lock()
time_condition_met = None
time_condition_scroll_met = None
length_2 = 45
y1_s_p = 0
y1_s_c = 0
start_point_scroll = 0
length_s_activate = 0
Delay_scroll = False
Scroll_ended = False



def volume_save():
    global vol
    global vol_p
    while True:
        time.sleep(2)
        with lock:
            vol_p = vol
def scroll_difference():
    global y1_s_p
    global y1_s_c
    while True:
        time.sleep(0.5)
        with lock:
            y1_s_p = y1_s_c
def scroll_wait():
    global Delay_scroll
    global Scroll_ended
    if Scroll_ended == True:
        time.sleep(2)
        with lock:
            Delay_scroll = False
        Scroll_ended = False
              

def scroll(img, lmList):
    global first_iteration_scroll
    global y1_s_p
    global y1_s_c
    global start_point_scroll
    global time_condition_scroll_met
    global length_s_activate
    global Scroll_on
    global Delay_scroll
    global Scroll_ended
    mouse_controller = mouse.Controller()
    if len(lmList) != 0  :
        x1, y1_s_c = lmList[12][1] , lmList[12][2]
        x2, y2 = lmList[8][1] , lmList[8][2]
        x3, y3 = lmList[9][1] , lmList[9][2]
        length_s = math.hypot(x2-x1,y2-y1_s_c)
        length_s_activate = math.hypot(x3-x1,y3-y1_s_c)
        height_dif = y1_s_c - y1_s_p


        if length_s < 30 and first_iteration_scroll and Delay_scroll != True:
            start_point_scroll = y1_s_c
            first_iteration_scroll = False 
            Scroll_on = True
            Delay_scroll = True

        if length_s < 30 and first_iteration_scroll !=True :
            cv2.line(img, (0,start_point_scroll+35),(0,start_point_scroll+80),(0,165,255),3)

            if height_dif > 0 and y1_s_c > start_point_scroll + 55 :
                mouse_controller.scroll(0, +1)  # Scroll down by one unit
            if height_dif < 0 and y1_s_c < start_point_scroll + 25 :
                mouse_controller.scroll(0, -1) 

             
        if start_point_scroll + 35 < y1_s_c < start_point_scroll + 80  :
            if time_condition_scroll_met is None:
                time_condition_scroll_met = time.time()
                # перевіряє чи виконується умова 2 сек
            elif time.time() - time_condition_scroll_met >= 2:
                first_iteration_scroll = True
                time_condition_scroll_met = None # збиває таймер
                Scroll_on = False
                Scroll_ended = True  #для того щоб starting point моментальне не мінявся і можна було розссунути пальці
        else:
                # якщо умова не виконана збиває таймер
                time_condition_scroll_met = None 
             


def volume_changing(img, lmList):
    
    global first_iteration_volume
    global vol
    global vol_p
    global time_condition_met
    global length_2
    global Volume_on
    if len(lmList) != 0 :
        
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
        if length < 50 and first_iteration_volume:
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
            first_iteration_volume = False 
            Volume_on = True   
            
            return vol , first_iteration_volume
        
        if  first_iteration_volume != True :
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
                    first_iteration_volume = True
                    time_condition_met = None
                    Volume_on = False  # збиває таймер
            else:
                # якщо умова не виконана збиває таймер
                time_condition_met = None 
            return vol
        
           

  
volume_save_thread = threading.Thread(target=volume_save, daemon=True)
volume_save_thread.start() 
scroll_difference_thread = threading.Thread(target=scroll_difference, daemon=True)
scroll_difference_thread.start()
scroll_wait_thread = threading.Thread(target=scroll_wait, daemon=True)
scroll_wait_thread.start()            
    
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    #fps_img = detector.Fps_m(img)
    lmList = detector.findPosition(img)
    if Scroll_on == False : 
        volume_c=volume_changing(img, lmList)
    if Volume_on == False :
        scroll(img, lmList)
    #print(start_point_scroll)
    #print(vol_p)
    #print(length_s_activate)
    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty("img", cv2.WND_PROP_VISIBLE)<1:
        break
    cv2.waitKey(1) 



    


