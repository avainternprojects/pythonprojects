"""
Comprehensive Eye Tracking System with Gaze Control
Features: Eye detection, gaze tracking, iris detection, calibration, 
user profiles, cursor control, click/scroll, and blink detection
"""

import cv2
import numpy as np
import os
import pickle
import json
import time
import pyautogui
from scipy.spatial import distance
from collections import deque
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import urllib.request
import bz2
import sys
import warnings
warnings.filterwarnings('ignore')

# Try to import dlib, if not available, use fallback method
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    print("dlib not installed. Will use fallback eye detection method.")
    DLIB_AVAILABLE = False

class EyeTrackerSystem:
    def __init__(self):
        # Initialize the main components
        self.camera = None
        self.DLIB_AVAILABLE = DLIB_AVAILABLE
        
        # Try to initialize dlib if available
        if self.DLIB_AVAILABLE:
            try:
                self.detector = dlib.get_frontal_face_detector()
                self.predictor = None  # Will be loaded later
            except Exception as e:
                print(f"Error initializing dlib: {e}")
                self.DLIB_AVAILABLE = False
        
        # Initialize OpenCV's face detector as fallback
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_eye.xml'
        )
        
        # Eye tracking variables
        self.eye_landmarks = {
            'left_eye': list(range(36, 42)),
            'right_eye': list(range(42, 48))
        }
        
        # Gaze estimation variables
        self.gaze_history = deque(maxlen=10)
        self.smoothed_gaze = (0, 0)
        self.screen_size = pyautogui.size()
        
        # Blink detection variables
        self.EAR_THRESHOLD = 0.25
        self.EAR_CONSEC_FRAMES = 3
        self.ear_history = deque(maxlen=5)
        self.blink_counter = 0
        self.blink_detected = False
        self.last_blink_time = time.time()
        self.blink_cooldown = 0.5  # seconds
        
        # Calibration variables
        self.calibration_points = []
        self.calibration_data = {
            'left': [],
            'right': []
        }
        self.calibration_model = None
        self.is_calibrated = False
        
        # User profile management
        self.current_user = None
        self.user_profiles = {}
        self.init_database()
        
        # Cursor control variables
        self.cursor_smoothing = 0.7
        self.scroll_speed = 20
        self.click_duration = 0.5  # seconds for dwell clicking
        self.click_start_time = None
        
        # Iris detection variables
        self.iris_detector = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        
        # Control flags
        self.running = False
        self.tracking_active = False
        self.click_mode = "blink"  # blink or dwell
        
        # Performance monitoring
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()
        
        # Try to load shape predictor
        if self.DLIB_AVAILABLE:
            self.load_shape_predictor()
    
    def load_shape_predictor(self):
        """Load dlib shape predictor (download if not exists)"""
        predictor_path = "shape_predictor_68_face_landmarks.dat"
        
        if not os.path.exists(predictor_path):
            print("Shape predictor file not found. Attempting to download...")
            try:
                # Try to download the file
                url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
                print(f"Downloading from {url}...")
                
                # Download with progress indicator
                def report_progress(block_num, block_size, total_size):
                    downloaded = block_num * block_size
                    if total_size > 0:
                        percent = min(100, downloaded * 100 / total_size)
                        sys.stdout.write(f"\rDownloading: {percent:.1f}%")
                        sys.stdout.flush()
                
                urllib.request.urlretrieve(url, predictor_path + ".bz2", report_progress)
                print("\nDownload complete. Extracting...")
                
                # Extract the file
                with bz2.BZ2File(predictor_path + ".bz2") as f_in, open(predictor_path, 'wb') as f_out:
                    f_out.write(f_in.read())
                
                # Remove the compressed file
                os.remove(predictor_path + ".bz2")
                print("Extraction complete!")
                
            except Exception as e:
                print(f"\nError downloading shape predictor: {e}")
                print("\nPlease download manually from:")
                print("http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2")
                print("Extract and place in the same directory as this script.")
                self.DLIB_AVAILABLE = False
                return
        
        try:
            self.predictor = dlib.shape_predictor(predictor_path)
            print("Shape predictor loaded successfully!")
        except Exception as e:
            print(f"Error loading shape predictor: {e}")
            self.DLIB_AVAILABLE = False
    
    def init_database(self):
        """Initialize SQLite database for user profiles"""
        try:
            self.conn = sqlite3.connect('eye_tracker_profiles.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Create users table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    created_date TEXT,
                    last_login TEXT,
                    calibration_points TEXT,
                    preferences TEXT
                )
            ''')
            self.conn.commit()
            
            # Create gaze data table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS gaze_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    timestamp TEXT,
                    gaze_x REAL,
                    gaze_y REAL,
                    screen_x INTEGER,
                    screen_y INTEGER,
                    pupil_size REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            self.conn.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Error initializing database: {e}")
    
    def eye_aspect_ratio(self, eye_points):
        """Calculate Eye Aspect Ratio for blink detection"""
        # Compute the euclidean distances between the vertical eye landmarks
        A = distance.euclidean(eye_points[1], eye_points[5])
        B = distance.euclidean(eye_points[2], eye_points[4])
        
        # Compute the euclidean distance between the horizontal eye landmarks
        C = distance.euclidean(eye_points[0], eye_points[3])
        
        # Compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)
        return ear
    
    def detect_face_fallback(self, frame):
        """Fallback face detection using OpenCV"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) > 0:
            # Return the largest face
            return max(faces, key=lambda rect: rect[2] * rect[3])
        return None
    
    def detect_eyes_fallback(self, frame, face_rect):
        """Fallback eye detection using OpenCV"""
        x, y, w, h = face_rect
        face_roi = frame[y:y+h, x:x+w]
        gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        
        eyes = self.eye_cascade.detectMultiScale(gray_face)
        
        eye_regions = []
        for (ex, ey, ew, eh) in eyes:
            # Adjust coordinates relative to original frame
            eye_regions.append((x + ex, y + ey, ew, eh))
        
        return eye_regions
    
    def extract_eye_region(self, frame, face_rect=None, eye_rect=None):
        """Extract eye region from frame using either dlib or OpenCV"""
        if eye_rect:
            x, y, w, h = eye_rect
            eye_roi = frame[y:y+h, x:x+w]
            return eye_roi, (x, y, w, h)
        
        return None, None
    
    def detect_iris(self, eye_roi):
        """Detect iris center in eye ROI"""
        if eye_roi is None or eye_roi.size == 0:
            return None, None
        
        try:
            # Convert to grayscale
            if len(eye_roi.shape) == 3:
                gray_eye = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)
            else:
                gray_eye = eye_roi
            
            # Apply CLAHE for better contrast
            gray_eye = self.iris_detector.apply(gray_eye)
            
            # Apply Gaussian blur
            gray_eye = cv2.GaussianBlur(gray_eye, (7, 7), 0)
            
            # Detect circles (iris)
            circles = cv2.HoughCircles(
                gray_eye,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=20,
                param1=50,
                param2=30,
                minRadius=5,
                maxRadius=30
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                # Get the most prominent circle
                iris = circles[0]
                return (iris[0], iris[1]), iris[2]
            
            # If Hough circles fail, try finding the darkest region (pupil)
            # This is a simpler fallback method
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray_eye)
            return min_loc, 5  # Approximate radius
            
        except Exception as e:
            # Fallback to simple darkest region detection
            try:
                gray_eye = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray_eye)
                return min_loc, 5
            except:
                return None, None
    
    def estimate_gaze(self, eye_roi, iris_center, eye_bbox):
        """Estimate gaze direction from iris position"""
        if iris_center is None:
            return None
        
        try:
            # Calculate iris position relative to eye ROI
            h, w = eye_roi.shape[:2]
            rel_x = (iris_center[0] / w) * 2 - 1  # Normalize to [-1, 1]
            rel_y = (iris_center[1] / h) * 2 - 1
            
            return (rel_x, rel_y)
        except:
            return None
    
    def calibrate(self):
        """Calibration procedure"""
        self.calibration_points = []
        
        # Define calibration points (9 points on screen)
        screen_w, screen_h = self.screen_size
        points = [
            (screen_w // 4, screen_h // 4),
            (screen_w // 2, screen_h // 4),
            (3 * screen_w // 4, screen_h // 4),
            (screen_w // 4, screen_h // 2),
            (screen_w // 2, screen_h // 2),
            (3 * screen_w // 4, screen_h // 2),
            (screen_w // 4, 3 * screen_h // 4),
            (screen_w // 2, 3 * screen_h // 4),
            (3 * screen_w // 4, 3 * screen_h // 4),
        ]
        
        # Create calibration window
        cv2.namedWindow('Calibration', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('Calibration', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        # Create a white background image
        calib_frame = np.ones((screen_h, screen_w, 3), dtype=np.uint8) * 255
        
        # Initialize camera if not already done
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
        
        for i, point in enumerate(points):
            # Show calibration point
            calib_frame_copy = calib_frame.copy()
            cv2.circle(calib_frame_copy, point, 20, (0, 0, 255), -1)
            cv2.putText(calib_frame_copy, f"Look at point {i+1}/9", 
                       (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
            
            cv2.imshow('Calibration', calib_frame_copy)
            cv2.waitKey(1000)  # Give user time to look at point
            
            # Collect gaze data for this point
            point_data = {'screen': point, 'gaze_samples': []}
            
            for _ in range(30):  # Collect 30 samples
                ret, frame = self.camera.read()
                if ret:
                    gaze = self.process_frame_for_calibration(frame)
                    if gaze:
                        point_data['gaze_samples'].append(gaze)
                cv2.waitKey(30)
            
            if point_data['gaze_samples']:
                # Average the gaze samples
                avg_gaze = np.mean(point_data['gaze_samples'], axis=0)
                self.calibration_data['left'].append((avg_gaze[0], point))
                self.calibration_data['right'].append((avg_gaze[1], point))
        
        cv2.destroyWindow('Calibration')
        
        # Fit polynomial regression model for gaze mapping
        self.calibration_model = self.fit_calibration_model()
        self.is_calibrated = True
        
        print("Calibration complete!")
        messagebox.showinfo("Calibration", "Calibration complete!")
    
    def fit_calibration_model(self):
        """Fit polynomial regression model for gaze mapping"""
        try:
            from sklearn.preprocessing import PolynomialFeatures
            from sklearn.linear_model import LinearRegression
            from sklearn.pipeline import Pipeline
            
            # Prepare data
            X_left = np.array([p[0] for p in self.calibration_data['left']])
            y_left = np.array([p[1] for p in self.calibration_data['left']])
            
            X_right = np.array([p[0] for p in self.calibration_data['right']])
            y_right = np.array([p[1] for p in self.calibration_data['right']])
            
            # Create polynomial regression models
            model_left = Pipeline([
                ('poly', PolynomialFeatures(degree=2)),
                ('linear', LinearRegression())
            ])
            
            model_right = Pipeline([
                ('poly', PolynomialFeatures(degree=2)),
                ('linear', LinearRegression())
            ])
            
            model_left.fit(X_left.reshape(-1, 2), y_left)
            model_right.fit(X_right.reshape(-1, 2), y_right)
            
            return {'left': model_left, 'right': model_right}
            
        except ImportError:
            print("scikit-learn not installed. Using simple mapping.")
            # Simple fallback mapping
            return {'left': None, 'right': None}
        except Exception as e:
            print(f"Error fitting calibration model: {e}")
            return None
    
    def process_frame_for_calibration(self, frame):
        """Process frame for calibration (simplified version)"""
        if self.DLIB_AVAILABLE and self.predictor:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector(gray)
            
            if len(faces) > 0:
                face = faces[0]
                landmarks = self.predictor(gray, face)
                
                left_gaze = None
                right_gaze = None
                
                # Process left eye
                left_eye_roi, left_bbox = self.extract_eye_region_with_landmarks(frame, landmarks, self.eye_landmarks['left_eye'])
                if left_eye_roi is not None:
                    left_iris, _ = self.detect_iris(left_eye_roi)
                    if left_iris:
                        left_gaze = self.estimate_gaze(left_eye_roi, left_iris, left_bbox)
                
                # Process right eye
                right_eye_roi, right_bbox = self.extract_eye_region_with_landmarks(frame, landmarks, self.eye_landmarks['right_eye'])
                if right_eye_roi is not None:
                    right_iris, _ = self.detect_iris(right_eye_roi)
                    if right_iris:
                        right_gaze = self.estimate_gaze(right_eye_roi, right_iris, right_bbox)
                
                if left_gaze and right_gaze:
                    return (left_gaze, right_gaze)
        else:
            # Fallback using OpenCV
            face_rect = self.detect_face_fallback(frame)
            if face_rect is not None:
                eyes = self.detect_eyes_fallback(frame, face_rect)
                if len(eyes) >= 2:
                    # Assume first two eyes are left and right
                    left_eye_roi, left_bbox = self.extract_eye_region(frame, None, eyes[0])
                    right_eye_roi, right_bbox = self.extract_eye_region(frame, None, eyes[1])
                    
                    if left_eye_roi is not None and right_eye_roi is not None:
                        left_iris, _ = self.detect_iris(left_eye_roi)
                        right_iris, _ = self.detect_iris(right_eye_roi)
                        
                        if left_iris and right_iris:
                            left_gaze = self.estimate_gaze(left_eye_roi, left_iris, left_bbox)
                            right_gaze = self.estimate_gaze(right_eye_roi, right_iris, right_bbox)
                            
                            if left_gaze and right_gaze:
                                return (left_gaze, right_gaze)
        
        return None
    
    def extract_eye_region_with_landmarks(self, frame, landmarks, eye_points):
        """Extract eye region using dlib landmarks"""
        eye_region = np.array([(landmarks.part(point).x, landmarks.part(point).y) 
                               for point in eye_points], dtype=np.int32)
        
        # Get bounding box
        x, y, w, h = cv2.boundingRect(eye_region)
        
        # Add padding
        padding = 10
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2*padding)
        h = min(frame.shape[0] - y, h + 2*padding)
        
        # Extract eye ROI
        eye_roi = frame[y:y+h, x:x+w]
        
        return eye_roi, (x, y, w, h)
    
    def detect_blink(self, landmarks=None, eyes=None):
        """Detect eye blink using Eye Aspect Ratio or simple method"""
        if self.DLIB_AVAILABLE and landmarks is not None:
            # Get eye landmarks
            left_eye = np.array([(landmarks.part(point).x, landmarks.part(point).y) 
                                for point in self.eye_landmarks['left_eye']])
            right_eye = np.array([(landmarks.part(point).x, landmarks.part(point).y) 
                                 for point in self.eye_landmarks['right_eye']])
            
            # Calculate EAR for both eyes
            left_ear = self.eye_aspect_ratio(left_eye)
            right_ear = self.eye_aspect_ratio(right_eye)
            ear = (left_ear + right_ear) / 2.0
        else:
            # Simplified blink detection using eye region size
            if eyes and len(eyes) >= 2:
                # Use eye height/width ratio as approximation
                left_eye_h = eyes[0][3]
                right_eye_h = eyes[1][3]
                ear = (left_eye_h + right_eye_h) / (2 * eyes[0][2])  # Approximate
            else:
                ear = 0.3  # Default value
        
        self.ear_history.append(ear)
        
        # Detect blink
        if ear < self.EAR_THRESHOLD:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.EAR_CONSEC_FRAMES:
                current_time = time.time()
                if current_time - self.last_blink_time > self.blink_cooldown:
                    self.blink_detected = True
                    self.last_blink_time = current_time
            self.blink_counter = 0
        
        return ear
    
    def map_gaze_to_screen(self, left_gaze, right_gaze):
        """Map gaze coordinates to screen coordinates using calibration model"""
        if not self.is_calibrated or left_gaze is None or right_gaze is None:
            return None
        
        try:
            # Average both eyes for better accuracy
            avg_gaze = [(left_gaze[i] + right_gaze[i]) / 2 for i in range(2)]
            
            if self.calibration_model and self.calibration_model['left'] is not None:
                # Use ML model
                screen_coords = self.calibration_model['left'].predict([avg_gaze])[0]
                screen_coords = (int(screen_coords[0]), int(screen_coords[1]))
            else:
                # Simple linear mapping as fallback
                screen_w, screen_h = self.screen_size
                screen_coords = (
                    int((avg_gaze[0] + 1) * screen_w / 2),
                    int((avg_gaze[1] + 1) * screen_h / 2)
                )
            
            # Ensure coordinates are within screen bounds
            screen_coords = (
                max(0, min(screen_coords[0], self.screen_size[0])),
                max(0, min(screen_coords[1], self.screen_size[1]))
            )
            
            return screen_coords
        except Exception as e:
            print(f"Error mapping gaze: {e}")
            return None
    
    def smooth_gaze(self, new_gaze):
        """Apply smoothing to gaze coordinates"""
        self.gaze_history.append(new_gaze)
        
        if len(self.gaze_history) < 2:
            return new_gaze
        
        # Apply exponential moving average
        smoothed = np.mean(self.gaze_history, axis=0)
        self.smoothed_gaze = (
            int(self.smoothed_gaze[0] * self.cursor_smoothing + smoothed[0] * (1 - self.cursor_smoothing)),
            int(self.smoothed_gaze[1] * self.cursor_smoothing + smoothed[1] * (1 - self.cursor_smoothing))
        )
        
        return self.smoothed_gaze
    
    def handle_cursor_control(self, screen_point):
        """Control mouse cursor based on gaze point"""
        if screen_point:
            try:
                pyautogui.moveTo(screen_point[0], screen_point[1])
            except Exception as e:
                print(f"Error moving cursor: {e}")
    
    def handle_click(self):
        """Handle click actions"""
        try:
            if self.click_mode == "blink" and self.blink_detected:
                pyautogui.click()
                self.blink_detected = False
                print("Click performed!")
            
            elif self.click_mode == "dwell":
                if self.click_start_time is None:
                    self.click_start_time = time.time()
                elif time.time() - self.click_start_time > self.click_duration:
                    pyautogui.click()
                    self.click_start_time = None
                    print("Dwell click performed!")
        except Exception as e:
            print(f"Error performing click: {e}")
    
    def handle_scroll(self, ear):
        """Handle scroll based on eye aspect ratio"""
        try:
            if ear < self.EAR_THRESHOLD * 0.8:  # More closed than blink threshold
                pyautogui.scroll(-self.scroll_speed)  # Scroll down
                time.sleep(0.1)
        except Exception as e:
            print(f"Error scrolling: {e}")
    
    def create_user_profile(self, username):
        """Create a new user profile"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Default preferences
        preferences = {
            'click_mode': 'blink',
            'scroll_speed': 20,
            'cursor_smoothing': 0.7,
            'ear_threshold': 0.25
        }
        
        try:
            self.cursor.execute('''
                INSERT INTO users (username, created_date, last_login, preferences)
                VALUES (?, ?, ?, ?)
            ''', (username, current_time, current_time, json.dumps(preferences)))
            self.conn.commit()
            
            # Get the user ID
            self.cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
            user_id = self.cursor.fetchone()[0]
            
            messagebox.showinfo("Success", f"Profile '{username}' created successfully!")
            return user_id
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", f"User {username} already exists!")
            return None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create profile: {e}")
            return None
    
    def load_user_profile(self, username):
        """Load an existing user profile"""
        try:
            self.cursor.execute('''
                SELECT id, username, preferences, calibration_points
                FROM users WHERE username = ?
            ''', (username,))
            
            result = self.cursor.fetchone()
            if result:
                user_id, username, preferences_json, calibration_json = result
                
                # Load preferences
                preferences = json.loads(preferences_json)
                self.click_mode = preferences.get('click_mode', 'blink')
                self.scroll_speed = preferences.get('scroll_speed', 20)
                self.cursor_smoothing = preferences.get('cursor_smoothing', 0.7)
                self.EAR_THRESHOLD = preferences.get('ear_threshold', 0.25)
                
                # Load calibration if exists
                if calibration_json:
                    self.calibration_data = json.loads(calibration_json)
                    self.is_calibrated = True
                    self.calibration_model = self.fit_calibration_model()
                
                # Update last login
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute('''
                    UPDATE users SET last_login = ? WHERE id = ?
                ''', (current_time, user_id))
                self.conn.commit()
                
                self.current_user = {
                    'id': user_id,
                    'username': username,
                    'preferences': preferences
                }
                
                messagebox.showinfo("Success", f"Loaded profile for {username}")
                return True
            
            messagebox.showerror("Error", f"Profile '{username}' not found!")
            return False
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load profile: {e}")
            return False
    
    def save_gaze_data(self, gaze_x, gaze_y, screen_x, screen_y, pupil_size):
        """Save gaze data to database for analysis"""
        if self.current_user:
            try:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute('''
                    INSERT INTO gaze_data (user_id, timestamp, gaze_x, gaze_y, screen_x, screen_y, pupil_size)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self.current_user['id'], current_time, gaze_x, gaze_y, screen_x, screen_y, pupil_size))
                self.conn.commit()
            except Exception as e:
                print(f"Error saving gaze data: {e}")
    
    def run_tracking(self):
        """Main tracking loop"""
        # Initialize camera
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            print("Error: Could not open camera")
            return
        
        print("Tracking started. Press 'q' to quit.")
        
        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                break
            
            self.frame_count += 1
            if self.frame_count % 30 == 0:
                elapsed_time = time.time() - self.start_time
                self.fps = self.frame_count / elapsed_time
            
            # Make a copy for display
            display_frame = frame.copy()
            
            if self.DLIB_AVAILABLE and self.predictor:
                # Use dlib for face detection
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.detector(gray)
                
                for face in faces:
                    landmarks = self.predictor(gray, face)
                    
                    # Detect eyes and iris using dlib landmarks
                    left_eye_roi, left_bbox = self.extract_eye_region_with_landmarks(frame, landmarks, self.eye_landmarks['left_eye'])
                    right_eye_roi, right_bbox = self.extract_eye_region_with_landmarks(frame, landmarks, self.eye_landmarks['right_eye'])
                    
                    # Detect iris
                    left_iris, left_iris_radius = self.detect_iris(left_eye_roi)
                    right_iris, right_iris_radius = self.detect_iris(right_eye_roi)
                    
                    # Estimate gaze
                    left_gaze = self.estimate_gaze(left_eye_roi, left_iris, left_bbox) if left_iris else None
                    right_gaze = self.estimate_gaze(right_eye_roi, right_iris, right_bbox) if right_iris else None
                    
                    # Detect blink
                    ear = self.detect_blink(landmarks=landmarks)
                    
                    # Draw face rectangle
                    x, y, w, h = (face.left(), face.top(), face.width(), face.height())
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
            else:
                # Use OpenCV fallback
                face_rect = self.detect_face_fallback(frame)
                if face_rect is not None:
                    x, y, w, h = face_rect
                    cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    
                    eyes = self.detect_eyes_fallback(frame, face_rect)
                    
                    left_gaze = None
                    right_gaze = None
                    left_bbox = None
                    right_bbox = None
                    
                    if len(eyes) >= 2:
                        # Assume first two eyes are left and right
                        left_eye_roi, left_bbox = self.extract_eye_region(frame, None, eyes[0])
                        right_eye_roi, right_bbox = self.extract_eye_region(frame, None, eyes[1])
                        
                        if left_eye_roi is not None and right_eye_roi is not None:
                            left_iris, left_iris_radius = self.detect_iris(left_eye_roi)
                            right_iris, right_iris_radius = self.detect_iris(right_eye_roi)
                            
                            if left_iris and right_iris:
                                left_gaze = self.estimate_gaze(left_eye_roi, left_iris, left_bbox)
                                right_gaze = self.estimate_gaze(right_eye_roi, right_iris, right_bbox)
                    
                    ear = self.detect_blink(eyes=eyes)
            
            # Map gaze to screen coordinates and control cursor
            if 'left_gaze' in locals() and 'right_gaze' in locals():
                if left_gaze and right_gaze:
                    screen_point = self.map_gaze_to_screen(left_gaze, right_gaze)
                    if screen_point:
                        # Smooth gaze
                        smoothed_point = self.smooth_gaze(screen_point)
                        
                        # Control cursor
                        self.handle_cursor_control(smoothed_point)
                        
                        # Save gaze data
                        pupil_size = (left_iris_radius + right_iris_radius) / 2 if 'left_iris_radius' in locals() and 'right_iris_radius' in locals() else 0
                        self.save_gaze_data(
                            (left_gaze[0] + right_gaze[0]) / 2,
                            (left_gaze[1] + right_gaze[1]) / 2,
                            smoothed_point[0], smoothed_point[1],
                            pupil_size
                        )
                        
                        # Draw gaze point on frame
                        cv2.circle(display_frame, (int(smoothed_point[0] * display_frame.shape[1] / self.screen_size[0]), 
                                                  int(smoothed_point[1] * display_frame.shape[0] / self.screen_size[1])), 
                                  5, (0, 255, 0), -1)
            
            # Handle click
            self.handle_click()
            
            # Draw annotations
            if 'left_bbox' in locals() and left_bbox:
                x, y, w, h = left_bbox
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if 'right_bbox' in locals() and right_bbox:
                x, y, w, h = right_bbox
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if 'left_iris' in locals() and left_iris and left_bbox:
                ix, iy = left_iris
                ix += left_bbox[0]
                iy += left_bbox[1]
                cv2.circle(display_frame, (ix, iy), 3, (0, 0, 255), -1)
            
            if 'right_iris' in locals() and right_iris and right_bbox:
                ix, iy = right_iris
                ix += right_bbox[0]
                iy += right_bbox[1]
                cv2.circle(display_frame, (ix, iy), 3, (0, 0, 255), -1)
            
            # Draw status information
            cv2.putText(display_frame, f"FPS: {self.fps:.1f}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if 'ear' in locals():
                cv2.putText(display_frame, f"EAR: {ear:.2f}", (10, 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            if self.blink_detected:
                cv2.putText(display_frame, "BLINK!", (10, 90), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if self.is_calibrated:
                cv2.putText(display_frame, "Calibrated", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(display_frame, "Not Calibrated", (10, 120), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            if self.current_user:
                cv2.putText(display_frame, f"User: {self.current_user['username']}", (10, 150), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            cv2.putText(display_frame, f"Mode: {self.click_mode} click", (10, 180), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Eye Tracking', display_frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        if self.camera:
            self.camera.release()
        cv2.destroyAllWindows()
    
    def run_gui(self):
        """Run the main GUI"""
        class EyeTrackerGUI:
            def __init__(self, tracker):
                self.tracker = tracker
                self.root = tk.Tk()
                self.root.title("Eye Tracking System")
                self.root.geometry("450x650")
                self.root.resizable(False, False)
                
                # Set icon if available
                try:
                    self.root.iconbitmap(default='icon.ico')
                except:
                    pass
                
                self.setup_ui()
                
            def setup_ui(self):
                # Style
                style = ttk.Style()
                style.theme_use('clam')
                
                # Title
                title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
                title_frame.pack(fill='x')
                title_frame.pack_propagate(False)
                
                title = tk.Label(title_frame, text="Eye Tracking Control Panel", 
                               font=("Arial", 16, "bold"), bg='#2c3e50', fg='white')
                title.pack(expand=True)
                
                # Main container
                main_container = tk.Frame(self.root, bg='#ecf0f1')
                main_container.pack(fill='both', expand=True, padx=10, pady=10)
                
                # User profile frame
                profile_frame = ttk.LabelFrame(main_container, text="User Profile", padding=10)
                profile_frame.pack(fill='x', pady=5)
                
                profile_inner = tk.Frame(profile_frame, bg='#ecf0f1')
                profile_inner.pack(fill='x')
                
                tk.Label(profile_inner, text="Username:", bg='#ecf0f1', font=('Arial', 10)).grid(row=0, column=0, sticky='w', padx=5)
                self.username_entry = tk.Entry(profile_inner, font=('Arial', 10), width=20)
                self.username_entry.grid(row=0, column=1, padx=5, pady=5)
                
                button_frame = tk.Frame(profile_inner, bg='#ecf0f1')
                button_frame.grid(row=1, column=0, columnspan=2, pady=5)
                
                self.create_btn = tk.Button(button_frame, text="Create Profile", 
                                          command=self.create_profile,
                                          bg='#27ae60', fg='white', font=('Arial', 10),
                                          width=12, cursor='hand2')
                self.create_btn.pack(side='left', padx=5)
                
                self.load_btn = tk.Button(button_frame, text="Load Profile", 
                                        command=self.load_profile,
                                        bg='#2980b9', fg='white', font=('Arial', 10),
                                        width=12, cursor='hand2')
                self.load_btn.pack(side='left', padx=5)
                
                # Control frame
                control_frame = ttk.LabelFrame(main_container, text="Controls", padding=10)
                control_frame.pack(fill='x', pady=5)
                
                control_inner = tk.Frame(control_frame, bg='#ecf0f1')
                control_inner.pack(fill='x')
                
                self.start_btn = tk.Button(control_inner, text="Start Tracking", 
                                         command=self.start_tracking,
                                         bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                                         width=15, height=2, cursor='hand2')
                self.start_btn.pack(side='left', padx=10, pady=5)
                
                self.stop_btn = tk.Button(control_inner, text="Stop Tracking", 
                                        command=self.stop_tracking,
                                        bg='#c0392b', fg='white', font=('Arial', 12, 'bold'),
                                        width=15, height=2, cursor='hand2',
                                        state='disabled')
                self.stop_btn.pack(side='left', padx=10, pady=5)
                
                # Calibration frame
                calib_frame = ttk.LabelFrame(main_container, text="Calibration", padding=10)
                calib_frame.pack(fill='x', pady=5)
                
                calib_inner = tk.Frame(calib_frame, bg='#ecf0f1')
                calib_inner.pack(fill='x')
                
                self.calib_btn = tk.Button(calib_inner, text="Start Calibration", 
                                         command=self.start_calibration,
                                         bg='#f39c12', fg='white', font=('Arial', 11, 'bold'),
                                         width=20, cursor='hand2')
                self.calib_btn.pack(pady=5)
                
                self.calib_status = tk.Label(calib_inner, text="● Not calibrated", 
                                           font=('Arial', 10), fg='red', bg='#ecf0f1')
                self.calib_status.pack()
                
                # Settings frame
                settings_frame = ttk.LabelFrame(main_container, text="Settings", padding=10)
                settings_frame.pack(fill='x', pady=5)
                
                settings_inner = tk.Frame(settings_frame, bg='#ecf0f1')
                settings_inner.pack(fill='x')
                
                # Click mode
                click_row = tk.Frame(settings_inner, bg='#ecf0f1')
                click_row.pack(fill='x', pady=5)
                
                tk.Label(click_row, text="Click Mode:", bg='#ecf0f1', 
                        font=('Arial', 10)).pack(side='left', padx=5)
                
                self.click_mode_var = tk.StringVar(value='blink')
                blink_rb = tk.Radiobutton(click_row, text='Blink', variable=self.click_mode_var, 
                                         value='blink', bg='#ecf0f1', font=('Arial', 10))
                blink_rb.pack(side='left', padx=10)
                
                dwell_rb = tk.Radiobutton(click_row, text='Dwell', variable=self.click_mode_var, 
                                         value='dwell', bg='#ecf0f1', font=('Arial', 10))
                dwell_rb.pack(side='left', padx=10)
                
                # Scroll speed
                scroll_row = tk.Frame(settings_inner, bg='#ecf0f1')
                scroll_row.pack(fill='x', pady=5)
                
                tk.Label(scroll_row, text="Scroll Speed:", bg='#ecf0f1', 
                        font=('Arial', 10)).pack(side='left', padx=5)
                
                self.scroll_speed_var = tk.IntVar(value=20)
                scroll_scale = tk.Scale(scroll_row, from_=5, to=50, orient='horizontal',
                                       variable=self.scroll_speed_var, length=200,
                                       bg='#ecf0f1', font=('Arial', 8))
                scroll_scale.pack(side='left', padx=10)
                
                # Cursor smoothing
                smooth_row = tk.Frame(settings_inner, bg='#ecf0f1')
                smooth_row.pack(fill='x', pady=5)
                
                tk.Label(smooth_row, text="Smoothing:", bg='#ecf0f1', 
                        font=('Arial', 10)).pack(side='left', padx=5)
                
                self.smoothing_var = tk.DoubleVar(value=0.7)
                smooth_scale = tk.Scale(smooth_row, from_=0.1, to=0.9, resolution=0.1,
                                       orient='horizontal', variable=self.smoothing_var,
                                       length=200, bg='#ecf0f1', font=('Arial', 8))
                smooth_scale.pack(side='left', padx=10)
                
                # Save settings button
                self.save_btn = tk.Button(settings_inner, text="Save Settings", 
                                        command=self.save_settings,
                                        bg='#3498db', fg='white', font=('Arial', 10),
                                        cursor='hand2')
                self.save_btn.pack(pady=10)
                
                # Status frame
                status_frame = ttk.LabelFrame(main_container, text="Status", padding=10)
                status_frame.pack(fill='x', pady=5)
                
                status_inner = tk.Frame(status_frame, bg='#ecf0f1')
                status_inner.pack(fill='x')
                
                self.status_label = tk.Label(status_inner, text="● System Ready", 
                                           font=('Arial', 11), fg='green', bg='#ecf0f1')
                self.status_label.pack()
                
                self.fps_label = tk.Label(status_inner, text="FPS: 0", 
                                        font=('Arial', 10), bg='#ecf0f1')
                self.fps_label.pack()
                
                self.ear_label = tk.Label(status_inner, text="EAR: 0.00", 
                                        font=('Arial', 10), bg='#ecf0f1')
                self.ear_label.pack()
                
                self.user_label = tk.Label(status_inner, text="No user loaded", 
                                         font=('Arial', 10), bg='#ecf0f1')
                self.user_label.pack()
                
                # Exit button
                exit_btn = tk.Button(main_container, text="Exit", command=self.exit_app,
                                   bg='#7f8c8d', fg='white', font=('Arial', 12, 'bold'),
                                   cursor='hand2')
                exit_btn.pack(pady=10)
            
            def create_profile(self):
                username = self.username_entry.get().strip()
                if username:
                    self.tracker.create_user_profile(username)
                else:
                    messagebox.showwarning("Warning", "Please enter a username!")
            
            def load_profile(self):
                username = self.username_entry.get().strip()
                if username:
                    if self.tracker.load_user_profile(username):
                        self.update_settings_display()
                        self.user_label.config(text=f"User: {username}")
                else:
                    messagebox.showwarning("Warning", "Please enter a username!")
            
            def update_settings_display(self):
                self.click_mode_var.set(self.tracker.click_mode)
                self.scroll_speed_var.set(self.tracker.scroll_speed)
                self.smoothing_var.set(self.tracker.cursor_smoothing)
            
            def save_settings(self):
                if self.tracker.current_user:
                    self.tracker.click_mode = self.click_mode_var.get()
                    self.tracker.scroll_speed = self.scroll_speed_var.get()
                    self.tracker.cursor_smoothing = self.smoothing_var.get()
                    
                    # Update database
                    preferences = {
                        'click_mode': self.tracker.click_mode,
                        'scroll_speed': self.tracker.scroll_speed,
                        'cursor_smoothing': self.tracker.cursor_smoothing,
                        'ear_threshold': self.tracker.EAR_THRESHOLD
                    }
                    
                    try:
                        self.tracker.cursor.execute('''
                            UPDATE users SET preferences = ? WHERE id = ?
                        ''', (json.dumps(preferences), self.tracker.current_user['id']))
                        self.tracker.conn.commit()
                        
                        messagebox.showinfo("Success", "Settings saved!")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save settings: {e}")
                else:
                    messagebox.showwarning("Warning", "Please load a profile first!")
            
            def start_calibration(self):
                if self.tracker.current_user:
                    # Run calibration in a separate thread to keep GUI responsive
                    def run_calibration():
                        self.calib_btn.config(state='disabled')
                        self.tracker.calibrate()
                        self.calib_btn.config(state='normal')
                        self.calib_status.config(text="● Calibrated", fg="green")
                        
                        # Save calibration data to database
                        if self.tracker.calibration_data:
                            try:
                                self.tracker.cursor.execute('''
                                    UPDATE users SET calibration_points = ? WHERE id = ?
                                ''', (json.dumps(self.tracker.calibration_data), self.tracker.current_user['id']))
                                self.tracker.conn.commit()
                            except Exception as e:
                                print(f"Error saving calibration: {e}")
                    
                    threading.Thread(target=run_calibration, daemon=True).start()
                else:
                    messagebox.showwarning("Warning", "Please load a profile first!")
            
            def start_tracking(self):
                if self.tracker.is_calibrated:
                    self.tracker.running = True
                    self.tracker.tracking_active = True
                    self.start_btn.config(state='disabled')
                    self.stop_btn.config(state='normal')
                    self.status_label.config(text="● Tracking Active", fg='green')
                    
                    # Start tracking in a separate thread
                    self.tracking_thread = threading.Thread(target=self.tracker.run_tracking, daemon=True)
                    self.tracking_thread.start()
                    
                    # Start status update
                    self.update_status()
                else:
                    messagebox.showwarning("Warning", "Please calibrate first!")
            
            def stop_tracking(self):
                self.tracker.running = False
                self.tracker.tracking_active = False
                self.start_btn.config(state='normal')
                self.stop_btn.config(state='disabled')
                self.status_label.config(text="● Tracking Stopped", fg='red')
            
            def update_status(self):
                if self.tracker.tracking_active:
                    self.fps_label.config(text=f"FPS: {self.tracker.fps:.1f}")
                    if self.tracker.ear_history:
                        self.ear_label.config(text=f"EAR: {self.tracker.ear_history[-1]:.3f}")
                    self.root.after(100, self.update_status)
            
            def exit_app(self):
                self.tracker.running = False
                if self.tracker.camera:
                    self.tracker.camera.release()
                cv2.destroyAllWindows()
                try:
                    self.tracker.conn.close()
                except:
                    pass
                self.root.quit()
                self.root.destroy()
            
            def run(self):
                self.root.mainloop()
        
        gui = EyeTrackerGUI(self)
        gui.run()

def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []
    
    try:
        import cv2
    except ImportError:
        missing.append("opencv-python")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import scipy
    except ImportError:
        missing.append("scipy")
    
    try:
        import pyautogui
    except ImportError:
        missing.append("pyautogui")
    
    try:
        import sklearn
    except ImportError:
        print("scikit-learn not installed. Calibration will use simple mapping.")
    
    if missing:
        print("\nMissing dependencies:")
        for m in missing:
            print(f"  - {m}")
        print("\nInstall them using:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def main():
    """Main function to run the eye tracking system"""
    print("=" * 50)
    print("Eye Tracking System")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return
    
    print("\nInitializing Eye Tracking System...")
    
    # Create eye tracker instance
    tracker = EyeTrackerSystem()
    
    # Run GUI
    tracker.run_gui()

if __name__ == "__main__":
    main()