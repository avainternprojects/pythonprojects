import numpy as np
import time
import pyautogui
from collections import deque
from scipy.spatial import distance
from config import cfg

class GazeTracker:
    """Handles gaze estimation, calibration, and mapping to screen"""
    
    def __init__(self, screen_size=None):
        self.screen_size = screen_size if screen_size else cfg.get_screen_size()
        
        # History for smoothing
        self.gaze_history = deque(maxlen=10)
        self.smoothed_gaze = (0, 0)
        
        # Calibration
        self.calibration_data = {'left': [], 'right': []}
        self.calibration_model = None
        self.is_calibrated = False
        
        # Blink detection
        self.blink_counter = 0
        self.last_blink_time = time.time()
        
    def estimate_gaze(self, eye_roi, iris_center):
        """Relative position of iris in eye ROI -> [-1, 1]"""
        if iris_center is None or eye_roi is None or eye_roi.size == 0:
            return None
        
        h, w = eye_roi.shape[:2]
        rel_x = (iris_center[0] / w) * 2 - 1
        rel_y = (iris_center[1] / h) * 2 - 1
        return (rel_x, rel_y)

    def calculate_ear(self, eye_landmarks):
        """Calculate Eye Aspect Ratio for blink detection"""
        if eye_landmarks is None: return 0.3
        
        # Convert landmarks to list of points if they aren't already
        points = eye_landmarks
        
        # Vertical distances
        A = distance.euclidean(points[1], points[5])
        B = distance.euclidean(points[2], points[4])
        # Horizontal distance
        C = distance.euclidean(points[0], points[3])
        
        return (A + B) / (2.0 * C)

    def calculate_ear_fallback(self, left_bbox, right_bbox):
        """Estimate EAR using bounding box height/width ratio when landmarks are missing"""
        if not left_bbox or not right_bbox: return 0.3
        
        # EAR approximation: height / width
        l_ear = left_bbox[3] / left_bbox[2]
        r_ear = right_bbox[3] / right_bbox[2]
        
        # Normalize: blinks roughly reach < 0.2
        # Usually eye height is 1/3 of width when open
        return (l_ear + r_ear) / 2.0

    def fit_model(self, calibration_data: dict) -> bool:
        """Fits a polynomial regression model from calibration data"""
        self.calibration_data = calibration_data
        try:
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            from sklearn.pipeline import Pipeline
            
            # Average left and right eye gaze for training
            # calibration_data['left'] is list of (gaze_normalized, screen_point)
            X_list = []
            y_list = []
            
            for i in range(len(self.calibration_data['left'])):
                l_gaze, screen_pt = self.calibration_data['left'][i]
                r_gaze, _ = self.calibration_data['right'][i]
                
                avg_gaze = [(l_gaze[0] + r_gaze[0]) / 2, (l_gaze[1] + r_gaze[1]) / 2]
                X_list.append(avg_gaze)
                y_list.append(screen_pt)
            
            X = np.array(X_list)
            y = np.array(y_list)
            
            model = Pipeline([
                ('poly', PolynomialFeatures(degree=2)),
                ('linear', LinearRegression())
            ])
            model.fit(X.reshape(-1, 2), y)
            
            self.calibration_model = model
            self.is_calibrated = True
            return True
        except Exception as e:
            print(f"Error fitting model: {e}")
            return False

    def process_blink(self, ear: float) -> bool:
        """Tracks consecutive frames of eye closure and returns True on blink release"""
        if ear < cfg.EAR_THRESHOLD_DEFAULT:
            self.blink_counter += 1
            return False
        else:
            # If we were previously in a blink state for enough frames
            if cfg.EAR_CONSEC_FRAMES_DEFAULT <= self.blink_counter < 15: # 15 frames is ~0.5s, avoids long closure
                self.blink_counter = 0
                current_time = time.time()
                if current_time - self.last_blink_time > cfg.BLINK_COOLDOWN_DEFAULT:
                    self.last_blink_time = current_time
                    return True
            self.blink_counter = 0
            return False

    def map_to_screen(self, left_gaze: tuple, right_gaze: tuple, smoothing: float = cfg.CURSOR_SMOOTHING_DEFAULT):
        """Maps gaze coordinates to pixel coordinates on screen"""
        if not self.is_calibrated or left_gaze is None or right_gaze is None:
            return None
        
        avg_gaze = [(left_gaze[0] + right_gaze[0]) / 2, (left_gaze[1] + right_gaze[1]) / 2]
        
        if self.calibration_model:
            screen_coords = self.calibration_model.predict([avg_gaze])[0]
            screen_x, screen_y = int(screen_coords[0]), int(screen_coords[1])
        else:
            # Fallback simple mapping
            sw, sh = self.screen_size
            screen_x = int((avg_gaze[0] + 1) * sw / 2)
            screen_y = int((avg_gaze[1] + 1) * sh / 2)
            
        # Bound to screen
        screen_x = max(0, min(screen_x, self.screen_size[0]))
        screen_y = max(0, min(screen_y, self.screen_size[1]))
        
        # Internal Smoothing (Exponential Moving Average)
        self.smoothed_gaze = (
            int(self.smoothed_gaze[0] * smoothing + screen_x * (1 - smoothing)),
            int(self.smoothed_gaze[1] * smoothing + screen_y * (1 - smoothing))
        )
        
        return self.smoothed_gaze

class ActionHandler:
    """Handles OS actions like clicking, scrolling, and cursor movement"""
    
    def __init__(self):
        pyautogui.FAILSAFE = False
        
    def move_cursor(self, point: tuple):
        if point:
            try:
                # Use a small duration to make movement smoother
                pyautogui.moveTo(point[0], point[1], duration=0.01)
            except Exception: 
                pass

    def perform_click(self, mode: str = "blink"):
        try:
            pyautogui.click()
            print("Click triggered!")
            return True
        except Exception: 
            return False

    def perform_scroll(self, amount: int):
        try:
            pyautogui.scroll(amount)
        except Exception: 
            pass
