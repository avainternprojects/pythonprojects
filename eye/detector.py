import cv2
import numpy as np
import os
import urllib.request
import bz2
import sys
from config import cfg

try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False

class EyeDetector:
    """Handles face, landmark, and iris detection using dlib or OpenCV fallback"""
    
    def __init__(self):
        self.dlib_available = False
        self.dlib_downloading = False
        self.detector = None
        self.predictor = None
        self.dlib_load_error = None
        
        # Fallback cascades (always loaded)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # CLAHE for contrast enhancement
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        
        # Optional dlib initialization
        if DLIB_AVAILABLE:
            if os.path.exists(cfg.SHAPE_PREDICTOR_PATH):
                self._init_dlib()
            elif cfg.DOWNLOAD_DLIB_AUTO:
                # This should be called from a thread in actual usage
                pass

    def _init_dlib(self):
        try:
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(cfg.SHAPE_PREDICTOR_PATH)
            self.dlib_available = True
            return True
        except Exception as e:
            self.dlib_load_error = str(e)
            self.dlib_available = False
            return False

    def download_dlib_async(self, progress_callback=None):
        """Downloads and extracts dlib predictor in a thread-safe way"""
        if self.dlib_downloading: return
        self.dlib_downloading = True
        
        try:
            def report(block_num, block_size, total_size):
                if progress_callback:
                    downloaded = block_num * block_size
                    percent = min(100, downloaded * 100 / total_size) if total_size > 0 else 0
                    progress_callback(percent)
            
            bz2_path = cfg.SHAPE_PREDICTOR_PATH + ".bz2"
            urllib.request.urlretrieve(cfg.SHAPE_PREDICTOR_URL, bz2_path, report)
            
            with bz2.BZ2File(bz2_path) as f_in, open(cfg.SHAPE_PREDICTOR_PATH, 'wb') as f_out:
                f_out.write(f_in.read())
            
            os.remove(bz2_path)
            self._init_dlib()
        except Exception as e:
            self.dlib_load_error = str(e)
        finally:
            self.dlib_downloading = False

    def detect_face(self, gray: np.ndarray):
        """Returns the largest face rectangle in the frame (optimized with scaling)"""
        # Scaling for speed if configured
        scale = cfg.FRAME_SCALE
        face_rect = None
        face_obj = None

        # Try with scaled image first for performance
        if scale < 1.0:
            small_gray = cv2.resize(gray, (0, 0), fx=scale, fy=scale)
            if self.dlib_available:
                faces = self.detector(small_gray)
                if len(faces) > 0:
                    face = faces[0]
                    face_rect = (int(face.left() / scale), int(face.top() / scale),
                                 int(face.width() / scale), int(face.height() / scale))
                    face_obj = dlib.rectangle(face_rect[0], face_rect[1], 
                                              face_rect[0] + face_rect[2], face_rect[1] + face_rect[3])
                    return face_rect, face_obj
            
            # OpenCV scaled fallback
            faces = self.face_cascade.detectMultiScale(small_gray, 1.1, 5)
            if len(faces) > 0:
                face = max(faces, key=lambda rect: rect[2] * rect[3])
                face_rect = (int(face[0] / scale), int(face[1] / scale),
                             int(face[2] / scale), int(face[3] / scale))
                return face_rect, None

        # If scaled failed or scale is 1.0, try full scale
        if self.dlib_available:
            faces = self.detector(gray)
            if len(faces) > 0:
                face = faces[0]
                face_rect = (face.left(), face.top(), face.width(), face.height())
                return face_rect, face
        
        # OpenCV full scale fallback
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5)
        if len(faces) > 0:
            face = max(faces, key=lambda rect: rect[2] * rect[3])
            face_rect = (face[0], face[1], face[2], face[3])
            return face_rect, None
            
        return None, None

    def get_landmarks(self, gray, face_obj):
        """Returns dlib landmarks for a face object"""
        if self.dlib_available and face_obj and self.predictor:
            return self.predictor(gray, face_obj)
        return None

    def get_eye_regions(self, frame, landmarks=None, face_rect=None):
        """Extracts eye regions (left, right) from frame"""
        if landmarks:
            left_roi, left_bbox = self._extract_eye_with_landmarks(frame, landmarks, cfg.EYE_LANDMARKS_LEFT)
            right_roi, right_bbox = self._extract_eye_with_landmarks(frame, landmarks, cfg.EYE_LANDMARKS_RIGHT)
            return (left_roi, left_bbox), (right_roi, right_bbox)
        
        if face_rect:
            x, y, w, h = face_rect
            face_roi = frame[y:y+h, x:x+w]
            gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
            eyes = self.eye_cascade.detectMultiScale(gray_face)
            
            if len(eyes) >= 2:
                # Sort by x coordinate to identify left/right roughly
                eyes = sorted(eyes, key=lambda e: e[0])
                left_eye = eyes[0]
                right_eye = eyes[1]
                
                def make_abs(eye):
                    ex, ey_rel, ew, eh = eye
                    return frame[y+ey_rel:y+ey_rel+eh, x+ex:x+ex+ew], (x+ex, y+ey_rel, ew, eh)
                
                return make_abs(left_eye), make_abs(right_eye)
        
        return (None, None), (None, None)

    def _extract_eye_with_landmarks(self, frame, landmarks, points_idx, padding=10):
        eye_points = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in points_idx], dtype=np.int32)
        x, y, w, h = cv2.boundingRect(eye_points)
        
        # Padding
        x = max(0, x - padding)
        y = max(0, y - padding)
        w = min(frame.shape[1] - x, w + 2*padding)
        h = min(frame.shape[0] - y, h + 2*padding)
        
        return frame[y:y+h, x:x+w], (x, y, w, h)

    def detect_iris(self, eye_roi: np.ndarray):
        """Detects iris center and radius in eye ROI"""
        if eye_roi is None or eye_roi.size == 0:
            return None, 0
        
        try:
            gray = cv2.cvtColor(eye_roi, cv2.COLOR_BGR2GRAY) if len(eye_roi.shape) == 3 else eye_roi
            gray = self.clahe.apply(gray)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            
            # Try HoughCircles
            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                param1=50, param2=30, minRadius=5, maxRadius=30
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                iris = circles[0]
                return (iris[0], iris[1]), iris[2]
            
            # Improved fallback: search for the centroid of the darkest 5% of pixels
            # This is usually the pupil/center of iris
            _, thresholded = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY_INV)
            moments = cv2.moments(thresholded)
            if moments["m00"] != 0:
                cx = int(moments["m10"] / moments["m00"])
                cy = int(moments["m01"] / moments["m00"])
                return (cx, cy), 8
            
            # Final fallback: darkest point
            _, _, min_loc, _ = cv2.minMaxLoc(gray)
            return min_loc, 5
        except Exception:
            return None, 0
