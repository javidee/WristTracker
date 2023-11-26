import cv2 
import  mediapipe as mp     
import time



class handDetector():
    def __init__(self,mode=False,maxHands=2,modelC=1,detectionCon=0.5,trackCon=0.5):
            self.mode = mode 
            self.maxHands = maxHands
            self.modelC=modelC
            self.detectionCon = detectionCon
            self.trackCon = trackCon
            
            self.mpHands = mp.solutions.hands
            self.hands = self.mpHands.Hands(self.mode, self.maxHands,self.modelC, self.detectionCon, self.trackCon)
            self.mpDraw = mp.solutions.drawing_utils #математичні обчислення щоб нанести на руку точки

    def findHands(self, img , draw = True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        #print(results.multi_hand_landmarks)
     
        if self.results.multi_hand_landmarks:
            for hand_Landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, hand_Landmarks, self.mpHands.HAND_CONNECTIONS) #малює точки
        return img
    

    def findPosition(self, img, handN=0, draw=True):
        lmList = []

        if self.results.multi_hand_landmarks:
            my_Hand = self.results.multi_hand_landmarks[handN]
         
            for id, lm in enumerate(my_Hand.landmark):
                #print(id,lm)   
                h, w, c = img.shape
                cx = int(lm.x*w)
                cy = int(lm.y*h)
                lmList.append([id, cx, cy])
                
        return lmList          
