import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import json
import os
from datetime import datetime
import time
import math

class EyeControlledMouse:
    def __init__(self):
        self.cam = cv2.VideoCapture(0)
        # Set camera resolution for better performance
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        self.face_mesh = mp.solutions.face_mesh.FaceMesh(
            refine_landmarks=True,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.screen_w, self.screen_h = pyautogui.size()
        
        # Gaze smoothing
        self.smoothing = 5
        self.gaze_history = []
        
        # Calibration parameters
        self.calibration_points = []
        self.calibration_data = {}
        self.calibrated = False
        self.calibration_matrix = None
        
        # User profiles
        self.profiles_dir = "user_profiles"
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
        self.current_user = None
        
        # Blink detection
        self.blink_counter = 0
        self.blink_threshold = 0.02
        self.last_blink_time = 0
        self.blink_cooldown = 0.3  # seconds
        
        # Click states
        self.click_enabled = True
        self.last_click_time = 0
        self.click_cooldown = 0.5
        
        # Scroll control
        self.scroll_enabled = True
        self.scroll_sensitivity = 50
        self.last_eye_y = None
        
        # Iris detection parameters
        self.iris_landmarks = [474, 475, 476, 477]  # Right eye iris landmarks
        
        # Gaze estimation
        self.gaze_ratio_threshold = 0.3
        
        # Current gaze position
        self.current_gaze_x = self.screen_w // 2
        self.current_gaze_y = self.screen_h // 2
        
        # Error message control
        self.last_error_time = 0
        self.error_cooldown = 2  # Show error messages every 2 seconds
        
    def detect_iris(self, landmarks, frame_w, frame_h):
        """Detect iris position using landmarks"""
        iris_points = []
        
        for idx in self.iris_landmarks:
            if idx < len(landmarks):
                landmark = landmarks[idx]
                x = int(landmark.x * frame_w)
                y = int(landmark.y * frame_h)
                iris_points.append((x, y))
            
        # Calculate iris center
        if len(iris_points) >= 3:  # Need at least 3 points for a reliable center
            iris_center = np.mean(iris_points, axis=0).astype(int)
            return iris_center, iris_points
        return None, None
    
    def estimate_gaze(self, landmarks, frame_w, frame_h):
        """Estimate gaze direction based on iris position relative to eye corners"""
        try:
            # Get eye landmarks (right eye as example)
            right_eye_indices = [33, 133, 158, 153, 144, 145, 153, 154]  # Eye contour
            
            # Calculate eye centers
            valid_indices = [i for i in right_eye_indices[:4] if i < len(landmarks)]
            if len(valid_indices) < 2:
                return None
                
            right_eye_center = np.mean([(landmarks[i].x, landmarks[i].y) for i in valid_indices], axis=0)
            
            # Get iris positions
            iris_center, _ = self.detect_iris(landmarks, frame_w, frame_h)
            
            if iris_center is not None:
                # Calculate gaze direction based on iris offset from eye center
                iris_x_norm = iris_center[0] / frame_w
                eye_center_x_norm = right_eye_center[0]
                
                gaze_offset = iris_x_norm - eye_center_x_norm
                
                if self.calibrated and 'x_coeffs' in self.calibration_data:
                    # Apply calibration transformation
                    calibrated_x = self.apply_calibration(gaze_offset)
                    return calibrated_x
                else:
                    # Simple gaze estimation
                    screen_x = self.screen_w * (0.5 + gaze_offset * 2)
                    screen_x = np.clip(screen_x, 0, self.screen_w)
                    return screen_x
            
            return None
            
        except Exception as e:
            # Rate-limit error messages
            current_time = time.time()
            if current_time - self.last_error_time > self.error_cooldown:
                print(f"Gaze estimation error: {e}")
                self.last_error_time = current_time
            return None
    
    def detect_blink(self, landmarks, eye_landmarks):
        """Detect eye blink using eye aspect ratio"""
        try:
            # Get eye landmarks
            valid_landmarks = []
            for idx in eye_landmarks[:6]:
                if idx < len(landmarks):
                    valid_landmarks.append(landmarks[idx])
            
            if len(valid_landmarks) < 6:
                return False
            
            # Calculate eye aspect ratio
            ear = self.calculate_ear(valid_landmarks)
            
            # Blink detection
            if ear < self.blink_threshold:
                self.blink_counter += 1
            else:
                if self.blink_counter > 2:  # Blink detected
                    current_time = time.time()
                    if current_time - self.last_blink_time > self.blink_cooldown:
                        self.last_blink_time = current_time
                        self.blink_counter = 0
                        return True
                self.blink_counter = 0
            return False
            
        except Exception as e:
            return False
    
    def calculate_ear(self, eye_points):
        """Calculate Eye Aspect Ratio"""
        try:
            # Vertical distances
            v1 = math.sqrt((eye_points[1].x - eye_points[5].x)**2 + (eye_points[1].y - eye_points[5].y)**2)
            v2 = math.sqrt((eye_points[2].x - eye_points[4].x)**2 + (eye_points[2].y - eye_points[4].y)**2)
            
            # Horizontal distance
            h = math.sqrt((eye_points[0].x - eye_points[3].x)**2 + (eye_points[0].y - eye_points[3].y)**2)
            
            # EAR formula
            ear = (v1 + v2) / (2.0 * h) if h > 0 else 0
            return ear
            
        except Exception as e:
            return 1.0  # Return high value if calculation fails
    
    def calibrate_gaze(self):
        """Calibration procedure with multiple points"""
        print("Starting calibration - Look at the dots on screen")
        print("Calibration will start in 3 seconds...")
        time.sleep(3)
        
        # Generate calibration points on screen
        points = []
        for y in [0.2, 0.5, 0.8]:
            for x in [0.2, 0.5, 0.8]:
                points.append((int(self.screen_w * x), int(self.screen_h * y)))
        
        calibration_data = []
        
        for i, point in enumerate(points):
            print(f"Calibration point {i+1}/{len(points)} - Look at the dot")
            
            # Move mouse to calibration point
            pyautogui.moveTo(point[0], point[1])
            
            # Wait for user to focus
            time.sleep(2)
            
            # Collect gaze data
            point_data = []
            for j in range(30):  # Collect 30 frames
                ret, frame = self.cam.read()
                if not ret:
                    continue
                    
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                output = self.face_mesh.process(rgb_frame)
                
                if output and output.multi_face_landmarks:
                    landmarks = output.multi_face_landmarks[0].landmark
                    h, w, _ = frame.shape
                    
                    # Get iris position
                    iris_center, _ = self.detect_iris(landmarks, w, h)
                    if iris_center is not None:
                        point_data.append({
                            'iris_x': iris_center[0] / w,
                            'iris_y': iris_center[1] / h,
                            'target_x': point[0] / self.screen_w,
                            'target_y': point[1] / self.screen_h
                        })
                
                time.sleep(0.03)
            
            if point_data:
                # Average the collected data
                avg_data = {
                    'iris_x': float(np.mean([d['iris_x'] for d in point_data])),
                    'iris_y': float(np.mean([d['iris_y'] for d in point_data])),
                    'target_x': point_data[0]['target_x'],
                    'target_y': point_data[0]['target_y']
                }
                calibration_data.append(avg_data)
                print(f"Point {i+1} calibrated")
        
        if len(calibration_data) >= 3:  # Need at least 3 points for calibration
            # Calculate calibration mapping
            self.calibration_data = self.calculate_calibration_mapping(calibration_data)
            self.calibrated = True
            print("Calibration complete!")
        else:
            print("Calibration failed - not enough data collected")
        
    def calculate_calibration_mapping(self, calibration_data):
        """Calculate mapping between iris position and screen coordinates"""
        iris_x = np.array([d['iris_x'] for d in calibration_data])
        iris_y = np.array([d['iris_y'] for d in calibration_data])
        target_x = np.array([d['target_x'] for d in calibration_data])
        target_y = np.array([d['target_y'] for d in calibration_data])
        
        # Polynomial fitting for more accurate mapping
        x_coeffs = np.polyfit(iris_x, target_x, 2)
        y_coeffs = np.polyfit(iris_y, target_y, 2)
        
        return {'x_coeffs': x_coeffs.tolist(), 'y_coeffs': y_coeffs.tolist()}
    
    def apply_calibration(self, iris_x, iris_y=None):
        """Apply calibration to raw gaze position"""
        if self.calibrated and 'x_coeffs' in self.calibration_data:
            calibrated_x = np.polyval(self.calibration_data['x_coeffs'], iris_x)
            if iris_y is not None and 'y_coeffs' in self.calibration_data:
                calibrated_y = np.polyval(self.calibration_data['y_coeffs'], iris_y)
                return calibrated_x, calibrated_y
            return calibrated_x
        return iris_x
    
    def save_profile(self, username):
        """Save user profile data"""
        profile_data = {
            'username': username,
            'calibration_data': self.calibration_data,
            'blink_threshold': self.blink_threshold,
            'scroll_sensitivity': self.scroll_sensitivity,
            'created_at': datetime.now().isoformat()
        }
        
        filename = os.path.join(self.profiles_dir, f"{username}.json")
        with open(filename, 'w') as f:
            json.dump(profile_data, f, indent=4)
        print(f"Profile saved for {username}")
    
    def load_profile(self, username):
        """Load user profile data"""
        filename = os.path.join(self.profiles_dir, f"{username}.json")
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                profile_data = json.load(f)
            
            self.calibration_data = profile_data['calibration_data']
            self.blink_threshold = profile_data['blink_threshold']
            self.scroll_sensitivity = profile_data['scroll_sensitivity']
            self.calibrated = True
            self.current_user = username
            print(f"Profile loaded for {username}")
            return True
        print(f"Profile not found for {username}")
        return False
    
    def smooth_gaze(self, x, y):
        """Apply temporal smoothing to gaze position"""
        self.gaze_history.append((x, y))
        if len(self.gaze_history) > self.smoothing:
            self.gaze_history.pop(0)
        
        if len(self.gaze_history) > 0:
            avg_x = np.mean([pos[0] for pos in self.gaze_history])
            avg_y = np.mean([pos[1] for pos in self.gaze_history])
            return float(avg_x), float(avg_y)
        return x, y
    
    def handle_scroll(self, eye_y):
        """Handle scrolling based on eye movement"""
        if self.last_eye_y is not None:
            diff = eye_y - self.last_eye_y
            
            if abs(diff) > 0.02:  # Threshold to avoid small movements
                if diff > 0:  # Eye moved down
                    pyautogui.scroll(-self.scroll_sensitivity)
                else:  # Eye moved up
                    pyautogui.scroll(self.scroll_sensitivity)
        
        self.last_eye_y = eye_y
    
    def run(self):
        """Main loop"""
        print("Eye Controlled Mouse")
        print("Commands:")
        print("  'c' - Calibrate")
        print("  's' - Save profile")
        print("  'l' - Load profile")
        print("  't' - Toggle click")
        print("  'v' - Toggle scroll")
        print("  'q' - Quit")
        
        frame_count = 0
        
        while True:
            ret, frame = self.cam.read()
            if not ret:
                print("Failed to grab frame")
                break
                
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            output = self.face_mesh.process(rgb_frame)
            landmark_points = output.multi_face_landmarks
            frame_h, frame_w, _ = frame.shape
            
            if landmark_points:
                landmarks = landmark_points[0].landmark
                
                # Iris detection and visualization
                iris_center, iris_points = self.detect_iris(landmarks, frame_w, frame_h)
                if iris_center is not None:
                    cv2.circle(frame, tuple(iris_center), 5, (0, 255, 0), -1)
                    
                    # Draw iris points
                    for point in iris_points:
                        cv2.circle(frame, point, 2, (0, 255, 255), -1)
                
                # Gaze estimation
                gaze_x = self.estimate_gaze(landmarks, frame_w, frame_h)
                if gaze_x is not None:
                    # Get eye position for scrolling
                    if 159 < len(landmarks):
                        eye_center_y = landmarks[159].y if self.scroll_enabled else None
                        
                        # Smooth gaze
                        smooth_x, _ = self.smooth_gaze(gaze_x, self.current_gaze_y)
                        self.current_gaze_x = smooth_x
                        
                        # Move cursor
                        pyautogui.moveTo(self.current_gaze_x, self.current_gaze_y)
                        
                        # Handle scroll
                        if self.scroll_enabled and eye_center_y is not None:
                            self.handle_scroll(eye_center_y)
                
                # Draw eye landmarks
                for idx in [33, 133, 158, 153, 144, 145, 153, 154]:  # Right eye
                    if idx < len(landmarks):
                        landmark = landmarks[idx]
                        x = int(landmark.x * frame_w)
                        y = int(landmark.y * frame_h)
                        cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)
                
                # Blink detection
                right_eye_landmarks = [33, 133, 158, 153, 144, 145]
                if self.detect_blink(landmarks, right_eye_landmarks):
                    if self.click_enabled:
                        current_time = time.time()
                        if current_time - self.last_click_time > self.click_cooldown:
                            pyautogui.click()
                            self.last_click_time = current_time
                            print("Click!")
                
                # Visual feedback for click
                if time.time() - self.last_click_time < 0.1:
                    cv2.putText(frame, "CLICK!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Display status
            status_y = 30
            cv2.putText(frame, f"Calibrated: {self.calibrated}", (10, status_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(frame, f"Click: {'ON' if self.click_enabled else 'OFF'}", (10, status_y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if self.click_enabled else (0, 0, 255), 2)
            cv2.putText(frame, f"Scroll: {'ON' if self.scroll_enabled else 'OFF'}", (10, status_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0) if self.scroll_enabled else (0, 0, 255), 2)
            
            # Show FPS
            frame_count += 1
            if frame_count % 30 == 0:
                cv2.putText(frame, "Press 'q' to quit", (10, frame_h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            cv2.imshow('Eye Controlled Mouse', frame)
            
            # Handle keyboard commands
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                self.calibrate_gaze()
            elif key == ord('s'):
                username = input("Enter username: ")
                self.save_profile(username)
            elif key == ord('l'):
                username = input("Enter username: ")
                self.load_profile(username)
            elif key == ord('t'):
                self.click_enabled = not self.click_enabled
                print(f"Click {'enabled' if self.click_enabled else 'disabled'}")
            elif key == ord('v'):
                self.scroll_enabled = not self.scroll_enabled
                print(f"Scroll {'enabled' if self.scroll_enabled else 'disabled'}")
        
        self.cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = EyeControlledMouse()
    controller.run()