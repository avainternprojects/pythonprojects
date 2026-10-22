import cv2
import numpy as np

def detect_all_colors(frame):
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Define comprehensive color ranges in HSV
    color_ranges = {
        'Red': [
            (np.array([0, 120, 70]), np.array([10, 255, 255])),
            (np.array([170, 120, 70]), np.array([180, 255, 255]))
        ],
        'Green': [
            (np.array([36, 50, 70]), np.array([89, 255, 255]))
        ],
        'Blue': [
            (np.array([90, 60, 60]), np.array([120, 255, 255]))
        ],
        'Yellow': [
            (np.array([20, 100, 100]), np.array([30, 255, 255]))
        ],
        'Orange': [
            (np.array([10, 100, 100]), np.array([20, 255, 255]))
        ],
        'Purple': [
            (np.array([120, 60, 60]), np.array([150, 255, 255]))
        ],
        'Pink': [
            (np.array([150, 40, 60]), np.array([170, 255, 255]))
        ],
        'Cyan': [
            (np.array([85, 60, 60]), np.array([95, 255, 255]))
        ],
        'White': [
            (np.array([0, 0, 200]), np.array([180, 30, 255]))
        ],
        'Gray': [
            (np.array([0, 0, 50]), np.array([180, 30, 200]))
        ],
        'Black': [
            (np.array([0, 0, 0]), np.array([180, 255, 30]))
        ]
    }
    
    # Create a blank image for color detection visualization
    height, width = frame.shape[:2]
    color_detection_map = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Process each color
    detected_colors = set()
    for color_name, ranges in color_ranges.items():
        # Create mask for this color
        mask = np.zeros_like(hsv[:,:,0])
        for lower, upper in ranges:
            mask = cv2.bitwise_or(mask, cv2.inRange(hsv, lower, upper))
        
        # Apply morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw on visualization map
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:  # Minimum area threshold
                detected_colors.add(color_name)
                
                # Create a colored mask for visualization
                if color_name == 'Red':
                    color_mask = (0, 0, 255)
                elif color_name == 'Green':
                    color_mask = (0, 255, 0)
                elif color_name == 'Blue':
                    color_mask = (255, 0, 0)
                elif color_name == 'Yellow':
                    color_mask = (0, 255, 255)
                elif color_name == 'Orange':
                    color_mask = (0, 165, 255)
                elif color_name == 'Purple':
                    color_mask = (128, 0, 128)
                elif color_name == 'Pink':
                    color_mask = (203, 192, 255)
                elif color_name == 'Cyan':
                    color_mask = (255, 255, 0)
                elif color_name == 'White':
                    color_mask = (255, 255, 255)
                elif color_name == 'Gray':
                    color_mask = (128, 128, 128)
                elif color_name == 'Black':
                    color_mask = (0, 0, 0)
                
                # Draw on visualization map
                color_detection_map[mask > 0] = color_mask
                
                # Draw on original frame
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(frame, (x, y), (x+w, y+h), color_mask, 2)
                cv2.putText(frame, color_name, (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Create a legend showing detected colors
    legend = np.zeros((150, 250, 3), dtype=np.uint8)
    cv2.putText(legend, "Detected Colors:", (10, 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    for i, color in enumerate(detected_colors):
        if color == 'Red':
            clr = (0, 0, 255)
        elif color == 'Green':
            clr = (0, 255, 0)
        elif color == 'Blue':
            clr = (255, 0, 0)
        elif color == 'Yellow':
            clr = (0, 255, 255)
        elif color == 'Orange':
            clr = (0, 165, 255)
        elif color == 'Purple':
            clr = (128, 0, 128)
        elif color == 'Pink':
            clr = (203, 192, 255)
        elif color == 'Cyan':
            clr = (255, 255, 0)
        elif color == 'White':
            clr = (255, 255, 255)
        elif color == 'Gray':
            clr = (128, 128, 128)
        elif color == 'Black':
            clr = (0, 0, 0)
        
        cv2.putText(legend, color, (10, 40 + i*20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, clr, 1)
    
    return frame, color_detection_map, legend

# Initialize webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Flip frame horizontally for mirror effect
    frame = cv2.flip(frame, 1)
    
    # Detect colors
    result, color_map, legend = detect_all_colors(frame)
    
    # Show the results
    cv2.imshow('Original with Detection', result)
    cv2.imshow('Color Detection Map', color_map)
    cv2.imshow('Legend', legend)
    
    # Exit on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()