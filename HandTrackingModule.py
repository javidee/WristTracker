import cv2 
import  mediapipe as mp     
import time



class handDetector():
    def __init__(self,mode=False,maxHands=2,modelC=1,detectionCon=0.5,trackCon=0.5):
            self.cTime = 0  # Initialize cTime
            self.pTime = 0
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
                     #print(0,".", cx, cy , cz) 
                     #if id == 0:
                         #cv2.circle(img, (cx, cy), 15, (255,0,255), cv2.FILLED )
    def Fps_m(self, img, cTime=0, pTime=0):

        self.cTime = time.time() #loop для фпс
        fps = 1/(self.cTime-self.pTime)
        self.pTime = self.cTime

        img_fps=cv2.putText(img, "Fps: " + str(int(fps)),(10,40) ,cv2.FONT_HERSHEY_PLAIN,2,(255,0,255),3)

        return img_fps
        
 


def main():
   
 
   cap =cv2.VideoCapture(0)
     
   detector = handDetector()

   while True:
    success, img = cap.read()
    
    img = detector.findHands(img) #надсилаю імг в метод класу детектор руки на обробку і повертаю.
    lmList = detector.findPosition(img)
    
    if len(lmList) !=0:
      print(lmList[4])

    Fps = detector.Fps_m(img)
    
    cv2.imshow("image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
     break
    if cv2.getWindowProperty("image", cv2.WND_PROP_VISIBLE)<1:
        break
    cv2.waitKey(1)



if __name__ == "__main__":
    main()