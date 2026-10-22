import cv2
import mediapipe as mp
import numpy as np
import tensorflow as tf

# Load trained model
model = tf.keras.models.load_model(r"C:\Users\vijay\Downloads\asl_alphabet_train.zip")

# MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)

# Label mapping
letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Extract hand region
            x_min = min([lm.x for lm in hand_landmarks.landmark]) * frame.shape[1]
            y_min = min([lm.y for lm in hand_landmarks.landmark]) * frame.shape[0]
            x_max = max([lm.x for lm in hand_landmarks.landmark]) * frame.shape[1]
            y_max = max([lm.y for lm in hand_landmarks.landmark]) * frame.shape[0]
            
            # Expand bounding box
            padding = 20
            x_min = max(0, int(x_min) - padding)
            y_min = max(0, int(y_min) - padding)
            x_max = min(frame.shape[1], int(x_max) + padding)
            y_max = min(frame.shape[0], int(y_max) + padding)
            
            hand_img = frame[y_min:y_max, x_min:x_max]
            
            if hand_img.size != 0:
                # Preprocess for model
                hand_img = cv2.resize(hand_img, (64, 64))
                hand_img = np.expand_dims(hand_img, axis=0) / 255.0
                
                # Predict
                pred = model.predict(hand_img)
                pred_letter = letters[np.argmax(pred)]
                confidence = np.max(pred)
                
                # Display prediction
                cv2.putText(frame, f"{pred_letter} ({confidence:.2f})", 
                            (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                            1, (0, 255, 0), 2)
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), 
                              (0, 255, 0), 2)
    
    cv2.imshow("Sign Language Detection", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()