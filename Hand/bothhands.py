import cv2
import mediapipe as mp
import math

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Initialize OpenCV
cap = cv2.VideoCapture(0)  # Use webcam

def calculate_distance(p1, p2):
    return math.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)

def get_hand_orientation(landmarks):
    # Check if hand is left or right based on wrist and pinky knuckle
    if landmarks[mp_hands.HandLandmark.WRIST].x < landmarks[mp_hands.HandLandmark.PINKY_MCP].x:
        return "LEFT"
    else:
        return "RIGHT"

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
            # Draw hand landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmark positions
            landmarks = []
            for lm in hand_landmarks.landmark:
                h, w, c = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                landmarks.append((cx, cy))

            # Determine hand (left/right)
            hand_type = handedness.classification[0].label  # 'Left' or 'Right'

            # Finger states (open/closed)
            thumb_open = False
            if hand_type == "Right":
                thumb_open = landmarks[4][0] < landmarks[3][0]  # Right thumb
            else:
                thumb_open = landmarks[4][0] > landmarks[3][0]  # Left thumb

            index_open = landmarks[8][1] < landmarks[6][1]
            middle_open = landmarks[12][1] < landmarks[10][1]
            ring_open = landmarks[16][1] < landmarks[14][1]
            pinky_open = landmarks[20][1] < landmarks[18][1]

            # Count open fingers
            finger_count = 0
            if thumb_open:
                finger_count += 1
            if index_open:
                finger_count += 1
            if middle_open:
                finger_count += 1
            if ring_open:
                finger_count += 1
            if pinky_open:
                finger_count += 1

            # Display hand type and finger count
            cv2.putText(frame, f'{hand_type} Hand - Fingers: {finger_count}', 
                        (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # Detect gestures (works for both hands)
            if finger_count == 2 and index_open and middle_open:
                cv2.putText(frame, "Peace Sign", (10, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            elif finger_count == 0:
                cv2.putText(frame, "Fist", (10, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            elif finger_count == 5:
                cv2.putText(frame, "Open Hand", (10, 100), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            elif finger_count == 1 and thumb_open:
                cv2.putText(frame, "Thumbs Up!", (10, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            elif finger_count == 3 and calculate_distance(landmarks[4], landmarks[8]) < 30:
                cv2.putText(frame, "OK Sign", (10, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow('Hand Gesture Recognition', frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()