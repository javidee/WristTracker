import cv2    
import time
import numpy as np
import HandTrackingModule as htm
import ctypes
import math
import threading
import pyautogui
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import mediapipe as mp 
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import win32gui
import pygetwindow as gw

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
vol_lock = threading.Lock()
time_condition_met = None
previous_gesture = None

def is_window_visible(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd != 0:
        return win32gui.IsWindowVisible(hwnd)
    else:
        return False

def maximize_all_windows():
    # Get all open windows
    windows = gw.getAllWindows()

    # Unminimize each window
    for window in windows:
        if window.isMinimized:
            window.restore()

def minimize_all_windows():
    # Get all open windows
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

    if lenghts[0][8] > lenghts[0][5] and lenghts[0][12] > lenghts[0][9] and lenghts[0][16] > lenghts[0][13] and lenghts[0][20] > lenghts[0][17] and (lenghts [4][17] > lenghts[5][17] and lenghts[4][5] > 30):
        return "opened"

def win_managment(lmlist):
    global previous_gesture
    if len(lmList) == 0:
        previous_gesture = None
    
    if is_fit_closed(lmList) == "closed":
        print("Fit is closed")
        print(previous_gesture)
        if previous_gesture == "open_fit":
            minimize_all_windows()
        previous_gesture = "closed_fit"
    elif is_fit_closed(lmlist) == "opened":
        print("Fit is opened")
        print(previous_gesture)
        if previous_gesture == "closed_fit":
            maximize_all_windows()
        previous_gesture = "open_fit"
        

        

def volume_save():
    global vol
    global vol_p
    while True:
        time.sleep(2)
        with vol_lock:
            vol_p = vol
              
    
def volume_changing(img, lmList):
    
    global first_iteration
    global vol
    global vol_p
    global time_condition_met
    if len(lmList) != 0  :
        
        #print(lmList[4],lmList[8])
        x1, y1 = lmList[4][1] , lmList[4][2]
        x2, y2 = lmList[8][1] , lmList[8][2]
        cx,cy = (x1+x2)//2, (y1+y2)//2
        length = math.hypot(x2-x1,y2-y1)
        if (length < 50 and first_iteration) or not first_iteration:
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
            #volume.SetMasterVolumeLevel(vol, None)
            cv2.rectangle(img, (5,int(vol_bar)), (35,475), (250, 0, 250), cv2.FILLED )
            if vol==-65:
                cv2.circle(img, (cx,cy), 5, (0,255,0), cv2.FILLED )
            if vol==0:
                cv2.circle(img, (x1,y1), 10, (0,0,255), cv2.FILLED )
                cv2.circle(img, (x2,y2), 10, (0,0,255), cv2.FILLED )
            first_iteration = False    
            
            return vol
        
volume_save_thread = threading.Thread(target=volume_save, daemon=True)
volume_save_thread.start()      


while True:
    success, img = cap.read()
    img = detector.findHands(img)
    #fps_img = detector.Fps_m(img)
    lmList = detector.findPosition(img)

    if lmList:
        win_managment(lmList)
    else: 
        previous_gesture = None
    
    volume_changing(img, lmList)
    cv2.rectangle(img, (0,150), (40, 480), (250, 250, 250), 5)

    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cv2.waitKey(1) 
    if cv2.getWindowProperty("img", cv2.WND_PROP_VISIBLE) < 1:
        break