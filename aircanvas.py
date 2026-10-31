import cv2
import numpy as np

# Initialize camera
cap = cv2.VideoCapture(0)

# Create canvas and temporary drawing layer
canvas = None
temp_layer = None

# Store previous point for line drawing
prev_point = None

# Drawing color (BGR format)
drawing_color = (255, 0, 0)  # Blue

# Color detection range (HSV - adjust for your marker)
lower_color = np.array([100, 150, 50])   # Lower HSV threshold (Blue)
upper_color = np.array([140, 255, 255])  # Upper HSV threshold (Blue)

# Brush settings
brush_size = 5
min_contour_area = 500  # Minimum size for detected object

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Flip the frame horizontally (mirror effect)
    frame = cv2.flip(frame, 1)

    # Initialize canvas and temp layer on first run
    if canvas is None:
        canvas = np.zeros_like(frame)
        temp_layer = np.zeros_like(frame)
    
    # Create a clean temporary layer each frame
    temp_layer.fill(0)

    # Convert BGR to HSV (better for color detection)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the selected color
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Remove noise
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # Find contours of the detected colored object
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # If contours are found, track the largest one
    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Only proceed if the contour is large enough
        if cv2.contourArea(largest_contour) > min_contour_area:
            (x, y, w, h) = cv2.boundingRect(largest_contour)
            center = (x + w // 2, y + h // 2)

            # Draw a circle around the detected object
            cv2.circle(frame, center, 10, (0, 255, 0), 2)

            # If previous point exists, draw a line
            if prev_point is not None:
                cv2.line(canvas, prev_point, center, drawing_color, brush_size)
                cv2.line(temp_layer, prev_point, center, drawing_color, brush_size)

            # Update previous point
            prev_point = center
        else:
            prev_point = None
    else:
        prev_point = None  # Reset if no object detected

    # Merge canvas, temp layer and camera frame
    result = cv2.addWeighted(frame, 1, canvas, 1, 0)
    result = cv2.add(result, temp_layer)

    # Add instructions
    cv2.putText(result, "Press 'c' to clear | 'q' to quit", (10, frame.shape[0]-10), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    # Show the result
    cv2.imshow("Air Canvas", result)

    # Handle keyboard input
    key = cv2.waitKey(1) & 0xFF
    if key == ord('c'):  # Clear canvas
        canvas.fill(0)
    elif key == ord('q'):  # Quit
        break

cap.release()
cv2.destroyAllWindows()