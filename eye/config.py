import os
import pyautogui

class Config:
    """Constants and configuration for the Eye Tracking System"""
    
    # Paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DB_PATH = os.path.join(BASE_DIR, 'eye_tracker_profiles.db')
    SHAPE_PREDICTOR_NAME = "shape_predictor_68_face_landmarks.dat"
    SHAPE_PREDICTOR_PATH = os.path.join(BASE_DIR, SHAPE_PREDICTOR_NAME)
    SHAPE_PREDICTOR_URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    
    # Eye tracking constants
    EYE_LANDMARKS_LEFT = list(range(36, 42))
    EYE_LANDMARKS_RIGHT = list(range(42, 48))
    
    # Detection thresholds
    EAR_THRESHOLD_DEFAULT = 0.25
    EAR_CONSEC_FRAMES_DEFAULT = 3
    BLINK_COOLDOWN_DEFAULT = 0.5  # seconds
    
    # Cursor control defaults
    CURSOR_SMOOTHING_DEFAULT = 0.7
    SCROLL_SPEED_DEFAULT = 20
    CLICK_DURATION_DEFAULT = 0.5  # seconds for dwell clicking
    
    # Colors (Modern Palette)
    COLOR_PRIMARY = "#2c3e50"    # Dark blue-gray
    COLOR_SECONDARY = "#3498db"  # Bright blue
    COLOR_SUCCESS = "#27ae60"    # Green
    COLOR_WARNING = "#f39c12"    # Orange
    COLOR_DANGER = "#c0392b"     # Red
    COLOR_BG = "#ecf0f1"         # Light gray
    COLOR_TEXT = "#2c3e50"       # Dark text
    COLOR_WHITE = "#ffffff"
    
    # Performance Settings
    FRAME_SCALE = 0.5  # Scale factor for processing (0.5 = 50% size)
    DOWNLOAD_DLIB_AUTO = False  # Don't auto-download on start
    
    @staticmethod
    def get_screen_size():
        return pyautogui.size()

# Global config instance
cfg = Config()
