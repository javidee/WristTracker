import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


def process_hand_landmarks(image):
    with mp_hands.Hands(static_image_mode=True, max_num_hands=1, min_detection_confidence=0.5) as hands:
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # Process the image
        results = hands.process(image_rgb)
        # Check for hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw the landmarks on the image
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(128,0,128), thickness=3, circle_radius=3))


cap = cv2.VideoCapture(0)  # Change the argument to the appropriate camera index
while True:
    ret, frame = cap.read()
    if not ret:
        break
    process_hand_landmarks(frame)
    cv2.imshow('Wrist Tracker', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
