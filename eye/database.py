import sqlite3
import json
from datetime import datetime
from config import cfg

class DatabaseManager:
    """Manages SQLite database operations for user profiles and gaze data"""
    
    def __init__(self, db_path=cfg.DB_PATH):
        self.db_path = db_path
        self._init_db()
        
    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)
        
    def _init_db(self):
        """Initialize tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                created_date TEXT,
                last_login TEXT,
                calibration_points TEXT,
                preferences TEXT
            )
        ''')
        
        # Gaze data table
        cursor.execute('''
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
        
        conn.commit()
        conn.close()

    def create_user(self, username):
        """Create a new user profile with default preferences"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        preferences = {
            'click_mode': 'blink',
            'scroll_speed': cfg.SCROLL_SPEED_DEFAULT,
            'cursor_smoothing': cfg.CURSOR_SMOOTHING_DEFAULT,
            'ear_threshold': cfg.EAR_THRESHOLD_DEFAULT
        }
        
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, created_date, last_login, preferences)
                VALUES (?, ?, ?, ?)
            ''', (username, current_time, current_time, json.dumps(preferences)))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_user(self, username):
        """Retrieve user profile by username"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, username, preferences, calibration_points
            FROM users WHERE username = ?
        ''', (username,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'username': row[1],
                'preferences': json.loads(row[2]),
                'calibration_data': json.loads(row[3]) if row[3] else None
            }
        return None

    def update_last_login(self, user_id):
        """Update last login timestamp for a user"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', (current_time, user_id))
        conn.commit()
        conn.close()

    def save_preferences(self, user_id, preferences):
        """Save user preferences"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET preferences = ? WHERE id = ?', (json.dumps(preferences), user_id))
        conn.commit()
        conn.close()

    def save_calibration(self, user_id, calibration_data):
        """Save calibration data for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET calibration_points = ? WHERE id = ?', (json.dumps(calibration_data), user_id))
        conn.commit()
        conn.close()

    def log_gaze_data(self, user_id, gaze_x, gaze_y, screen_x, screen_y, pupil_size):
        """Log gaze sample to database"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO gaze_data (user_id, timestamp, gaze_x, gaze_y, screen_x, screen_y, pupil_size)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, current_time, gaze_x, gaze_y, screen_x, screen_y, pupil_size))
        conn.commit()
        conn.close()
