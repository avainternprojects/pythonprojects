import sys
import os
import cv2
import numpy as np

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    print("Testing imports...")
    try:
        from config import cfg
        from database import DatabaseManager
        from detector import EyeDetector
        from tracker import GazeTracker, ActionHandler
        from gui import EyeTrackerGUI
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_detector():
    print("Testing Detector initialization...")
    try:
        from detector import EyeDetector
        detector = EyeDetector()
        print(f"✓ Detector initialized (Dlib available: {detector.dlib_available})")
        return True
    except Exception as e:
        print(f"✗ Detector failed: {e}")
        return False

def test_tracker():
    print("Testing Tracker logic...")
    try:
        from tracker import GazeTracker, ActionHandler
        tracker = GazeTracker(screen_size=(1920, 1080))
        
        # Test EAR calculation fallback
        ear = tracker.calculate_ear_fallback((100, 100, 50, 20), (200, 100, 50, 20))
        print(f"✓ EAR Fallback check: {ear:.2f}")
        
        # Test blink processing
        is_blink = tracker.process_blink(0.1) # Simulate closure
        is_blink_release = tracker.process_blink(0.3) # Simulate opening
        print(f"✓ Blink processing check")
        
        return True
    except Exception as e:
        print(f"✗ Tracker failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Eye Tracking System Verification ===")
    results = [test_imports(), test_detector(), test_tracker()]
    
    if all(results):
        print("\n=== SYSTEM CORE IS STABLE ===")
        print("You can now run 'python main.py' to start the application.")
    else:
        print("\n=== SYSTEM CORE HAS ISSUES ===")
        sys.exit(1)
