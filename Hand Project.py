import cv2
import HandTrackingModule as htm
import math
import win32gui
import pygetwindow as gw

wCam, hCam = 640, 480

cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(detectionCon=0.8)

previous_gesture = None
all_minimized_windows = []
last_active = None

def is_window_visible(window_title):
    hwnd = win32gui.FindWindow(None, window_title)
    if hwnd != 0:
        return win32gui.IsWindowVisible(hwnd)
    else:
        return False

def maximize_all_windows():
    # Get all open windows
    global all_minimized_windows
    global last_active
    windows = all_minimized_windows

    # Unminimize each window
    for window in windows:
        if window == last_active:
            continue
        if window.isMinimized:
            window.restore()
            all_minimized_windows.remove(window)
    last_active.restore()
    all_minimized_windows.remove(last_active)

def minimize_all_windows():
    # Get all open windows
    global last_active
    last_active = gw.getActiveWindow()
    windows = gw.getAllWindows()

    # Minimize each window
    for window in windows:
        if is_window_visible(window.title):
            all_minimized_windows.append(window)
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
    if len(lmList) == 0:
        previous_gesture = None
    
    if is_fit_closed(lmList) == "closed":
        if previous_gesture == "open_fit":
            minimize_all_windows()
        previous_gesture = "closed_fit"
    elif is_fit_closed(lmlist) == "opened":
        if previous_gesture == "closed_fit":
            maximize_all_windows()
        previous_gesture = "open_fit"
        
while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if lmList:
        win_managment(lmList)
    else: 
        previous_gesture = None

    cv2.imshow("img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    cv2.waitKey(1) 
    if cv2.getWindowProperty("img", cv2.WND_PROP_VISIBLE) < 1:
        break