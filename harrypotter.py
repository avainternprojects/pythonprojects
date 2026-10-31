import cv2
import numpy as np
import time

# Initialize webcam
cap = cv2.VideoCapture(0)

# Allow camera to warm up
time.sleep(2)

# Capture the background (stand out of frame first)
background = None
for _ in range(30):
    ret, background = cap.read()
background = cv2.flip(background, 1)  # Flip for mirror effect

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)  # Flip for mirror effect

    # Convert to HSV (better color detection)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range for green color (Harry Potter cloak)
    lower_green = np.array([35, 50, 50])   # Lower HSV threshold
    upper_green = np.array([85, 255, 255])  # Upper HSV threshold

    # Create a mask (detect green regions)
    mask = cv2.inRange(hsv, lower_green, upper_green)

    # Refine mask (remove noise)
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_DILATE, kernel, iterations=1)

    # Invert mask (cloak area = 0, non-cloak area = 1)
    mask_inv = cv2.bitwise_not(mask)

    # Apply mask to frame and background
    cloak_removed = cv2.bitwise_and(background, background, mask=mask)
    remaining_frame = cv2.bitwise_and(frame, frame, mask=mask_inv)

    # Combine to create invisibility effect
    final_output = cv2.add(cloak_removed, remaining_frame)

    # Display results
    cv2.imshow("Invisible Cloak", final_output)
    cv2.imshow("Original", frame)

    # Exit on 'ESC'
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()