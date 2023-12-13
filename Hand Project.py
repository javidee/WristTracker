import cv2    
import time
import numpy as np
import HandTrackingModule as htm
import ctypes
import math
import win32gui
import pygetwindow as gw
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
min_vol = -65
max_vol = 0
vol_bar= 0
first_iteration = True
vol = 0
vol_p = 0
lock = threading.Lock()
time_condition_met = None
length_2 = 45
previous_gesture = None
all_minimized_windows = []
last_active = None
Volume_on = False

def is_window_visible(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd != 0:
        return win32gui.IsWindowVisible(hwnd)
    else:
        return False

def maximize_all_windows():
    # Get all open windows
    global last_active
    
    last_active.restore()

def minimize_all_windows():
    # Get all open windows
    global last_active
    last_active = gw.getActiveWindow()
    windows = gw.getAllWindows()

    # Minimize each window
    for window in windows:
        if is_window_visible(window.title):
            window.minimize()

def is_fit_closed(lmlist):
    X_coordinates = []
    Y_coordinates = []


    for i in range(21):
        X_coordinates.append(lmList[i][1])
        Y_coordinates.append(lmList[i][2])

    lenghts = []

    for i in range(21):
        row = []
        for j in range(21):
            row.append(math.hypot(X_coordinates[i] - X_coordinates[j], Y_coordinates[i] - Y_coordinates[j]))
        lenghts.append(row)

    if lenghts[0][5] > lenghts[0][8] and lenghts[0][9] > lenghts[0][12] and lenghts[0][13] > lenghts[0][16] and lenghts[0][17] > lenghts[0][20] and (lenghts[4][17] < lenghts[5][17] or lenghts[4][5] < 30):
        return "closed"

    elif lenghts[0][8] > lenghts[0][5] and lenghts[0][12] > lenghts[0][9] and lenghts[0][16] > lenghts[0][13] and lenghts[0][20] > lenghts[0][17] and (lenghts [4][17] > lenghts[5][17] and lenghts[4][5] > 30) and lenghts[5][8] > 30 and lenghts[9][12] > 30 and lenghts[13][16] > 30 and lenghts[17][20] > 30:
        return "opened"

    else: 
        return None
    
def win_managment(lmlist):
    global previous_gesture
    global Volume_on
    if len(lmList) == 0:
        previous_gesture = None
        return
    

    if is_fit_closed(lmList) == "closed":
        if previous_gesture == "open_fit":
            minimize_all_windows()
        previous_gesture = "closed_fit"
    elif is_fit_closed(lmlist) == "opened":
        if previous_gesture == "closed_fit":
            maximize_all_windows()
        previous_gesture = "open_fit"


def volume_save():
    global vol
    global vol_p
    global Volume_on
    while True:
        time.sleep(2)
        with lock:
            vol_p = vol
            Volume_on = False
              
    
def volume_changing(img, lmList):
    global first_iteration
    global vol
    global vol_p
    global time_condition_met
    global length_2
    if len(lmList) != 0  :
        
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
        length = math.hypot(x2-x1,y2-y1)/k
        if length < 50 and first_iteration and is_fit_closed(lmList) != "closed":
            cv2.circle(img, (x1,y1), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (x2,y2), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (cx,cy), 5, (255,0,255), cv2.FILLED )
            cv2.line(img, (x1,y1),(x2,y2),(0,165,255),3)

            vol = np.interp(length,[50,300],[min_vol, max_vol])
            vol_bar = np.interp(length,[50,300],[475,155])
            volume.SetMasterVolumeLevel(vol, None)
            if vol==-65:
                cv2.circle(img, (cx,cy), 5, (0,255,0), cv2.FILLED )
            if vol==0:
                cv2.circle(img, (x1,y1), 10, (0,0,255), cv2.FILLED )
                cv2.circle(img, (x2,y2), 10, (0,0,255), cv2.FILLED )
            first_iteration = False

            return vol , first_iteration 
        
        if not first_iteration:
            x1, y1 = lmList[4][1] , lmList[4][2]
            x2, y2 = lmList[8][1] , lmList[8][2]
            cx,cy = (x1+x2)//2, (y1+y2)//2
            length =math.hypot(x2-x1,y2-y1)/k
            cv2.circle(img, (x1,y1), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (x2,y2), 10, (255,0,255), cv2.FILLED )
            cv2.circle(img, (cx,cy), 5, (255,0,255), cv2.FILLED )
            cv2.line(img, (x1,y1),(x2,y2),(0,165,255),3)
            vol = np.interp(length,[50,300],[min_vol, max_vol])
            vol_bar = np.interp(length,[50,300],[475,155])
            volume.SetMasterVolumeLevel(vol, None)
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
    lmList = detector.findPosition(img)
    
    volume_changing(img, lmList)
    win_managment(lmList) 

    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if cv2.getWindowProperty("img", cv2.WND_PROP_VISIBLE)<1:
        break
    cv2.waitKey(1) 
