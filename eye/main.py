import cv2
import time
import threading
import numpy as np
from config import cfg
from database import DatabaseManager
from detector import EyeDetector
from tracker import GazeTracker, ActionHandler
from gui import EyeTrackerGUI

class EyeTrackerController:
    """Main controller that orchestrates the eye tracking system"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.detector = EyeDetector()
        self.tracker = GazeTracker()
        self.actions = ActionHandler()
        
        self.current_user = None
        self.running = False
        self.camera = None
        self.gui = EyeTrackerGUI(self)
        
        # FPS calculation
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()

    def create_profile(self, username):
        if not username: return False
        user_id = self.db.create_user(username)
        return user_id is not None

    def load_profile(self, username):
        user_data = self.db.get_user(username)
        if user_data:
            self.current_user = user_data
            # Load preferences into tracker
            prefs = user_data['preferences']
            self.tracker.is_calibrated = user_data['calibration_data'] is not None
            if self.tracker.is_calibrated:
                self.tracker.fit_model(user_data['calibration_data'])
            return True
        return False

    def update_preferences(self, prefs):
        if self.current_user:
            self.db.save_preferences(self.current_user['id'], prefs)
            self.current_user['preferences'] = prefs

    def start_tracking(self):
        if not self.tracker.is_calibrated:
            return False
        
        self.running = True
        self.camera = cv2.VideoCapture(0)
        threading.Thread(target=self._tracking_loop, daemon=True).start()
        return True

    def stop_tracking(self):
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None

    def _tracking_loop(self):
        while self.running:
            ret, frame = self.camera.read()
            if not ret: break
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            face_rect, face_obj = self.detector.detect_face(gray)
            
            display_frame = frame.copy()
            
            if face_rect:
                # Draw face
                x, y, w, h = face_rect
                cv2.rectangle(display_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                landmarks = self.detector.get_landmarks(gray, face_obj)
                (left_roi, left_bbox), (right_roi, right_bbox) = self.detector.get_eye_regions(frame, landmarks, face_rect)
                
                # Detect Iris and Gaze
                left_iris, l_rad = self.detector.detect_iris(left_roi)
                right_iris, r_rad = self.detector.detect_iris(right_roi)
                
                # Draw Iris for debugging
                if left_iris:
                    cv2.circle(display_frame, (left_bbox[0] + left_iris[0], left_bbox[1] + left_iris[1]), 3, (0, 255, 0), -1)
                if right_iris:
                    cv2.circle(display_frame, (right_bbox[0] + right_iris[0], right_bbox[1] + right_iris[1]), 3, (0, 255, 0), -1)

                left_gaze = self.tracker.estimate_gaze(left_roi, left_iris)
                right_gaze = self.tracker.estimate_gaze(right_roi, right_iris)
                
                # Map Gaze to Screen
                if left_gaze and right_gaze:
                    screen_point = self.tracker.map_to_screen(left_gaze, right_gaze)
                    if screen_point:
                        self.actions.move_cursor(screen_point)
                        # Log gaze data
                        self.db.log_gaze_data(self.current_user['id'], screen_point[0], screen_point[1], 
                                            screen_point[0], screen_point[1], (l_rad + r_rad)/2)
                
                # Blink Detection for Click
                ear = 0.3
                if landmarks:
                    left_ear = self.tracker.calculate_ear([(landmarks.part(i).x, landmarks.part(i).y) for i in cfg.EYE_LANDMARKS_LEFT])
                    right_ear = self.tracker.calculate_ear([(landmarks.part(i).x, landmarks.part(i).y) for i in cfg.EYE_LANDMARKS_RIGHT])
                    ear = (left_ear + right_ear) / 2
                else:
                    # Fallback blink detection using ROI height
                    ear = self.tracker.calculate_ear_fallback(left_bbox, right_bbox)
                
                # Use robust blink processing
                if self.tracker.process_blink(ear):
                    self.actions.perform_click()
            else:
                if self.frame_count % 30 == 0:
                    print("Warning: Face not detected")
                
            # Update GUI (Thread-safe)
            self.gui.update_video(display_frame)
            self._update_fps()
            self.gui.update_stats(self.fps)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.stop_tracking()
                break
            
            # Small sleep to prevent CPU hogging
            time.sleep(0.01)

    def _update_fps(self):
        self.frame_count += 1
        if self.frame_count % 30 == 0:
            elapsed = time.time() - self.start_time
            if elapsed > 0:
                self.fps = self.frame_count / elapsed

    def run_calibration(self):
        """Runs the calibration process"""
        # 9 Point calibration logic
        screen_w, screen_h = cfg.get_screen_size()
        points = [
            (screen_w // 4, screen_h // 4), (screen_w // 2, screen_h // 4), (3 * screen_w // 4, screen_h // 4),
            (screen_w // 4, screen_h // 2), (screen_w // 2, screen_h // 2), (3 * screen_w // 4, screen_h // 2),
            (screen_w // 4, 3 * screen_h // 4), (screen_w // 2, 3 * screen_h // 4), (3 * screen_w // 4, 3 * screen_h // 4),
        ]
        
        calib_data = {'left': [], 'right': []}
        temp_cam = cv2.VideoCapture(0)
        
        cv2.namedWindow('Calibration', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Calibration', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        for i, point in enumerate(points):
            bg = np.ones((screen_h, screen_w, 3), dtype=np.uint8) * 255
            cv2.circle(bg, point, 20, (0, 0, 255), -1)
            cv2.putText(bg, f"Point {i+1}/9: Focus here", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
            cv2.imshow('Calibration', bg)
            cv2.waitKey(1000)
            
            samples_l, samples_r = [], []
            for _ in range(20):
                ret, frame = temp_cam.read()
                if ret:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    face_rect, face_obj = self.detector.detect_face(gray)
                    if face_rect:
                        landmarks = self.detector.get_landmarks(gray, face_obj)
                        (l_roi, _), (r_roi, _) = self.detector.get_eye_regions(frame, landmarks, face_rect)
                        l_iris, _ = self.detector.detect_iris(l_roi)
                        r_iris, _ = self.detector.detect_iris(r_roi)
                        l_gaze = self.tracker.estimate_gaze(l_roi, l_iris)
                        r_gaze = self.tracker.estimate_gaze(r_roi, r_iris)
                        if l_gaze: samples_l.append(l_gaze)
                        if r_gaze: samples_r.append(r_gaze)
                cv2.waitKey(20)
            
            if samples_l and samples_r:
                calib_data['left'].append((np.mean(samples_l, axis=0).tolist(), point))
                calib_data['right'].append((np.mean(samples_r, axis=0).tolist(), point))

        cv2.destroyWindow('Calibration')
        temp_cam.release()
        
        if self.tracker.fit_model(calib_data):
            self.db.save_calibration(self.current_user['id'], calib_data)
            return True
        return False

    def run(self):
        self.gui.run()

if __name__ == "__main__":
    controller = EyeTrackerController()
    controller.run()
