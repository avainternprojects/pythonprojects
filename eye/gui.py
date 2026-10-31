import tkinter as tk
from tkinter import ttk, messagebox
import threading
import cv2
import PIL.Image, PIL.ImageTk
from queue import Queue, Empty
from config import cfg

class EyeTrackerGUI:
    """Modern GUI for Eye Tracking System"""
    
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Eye Tracking System v2")
        self.root.geometry("1100x750")
        self.root.configure(bg=cfg.COLOR_BG)
        
        # Queue for thread-safe UI updates
        self.update_queue = Queue()
        
        self.setup_styles()
        self.create_widgets()
        
        # Start the queue processing loop
        self.root.after(100, self._process_queue)
        
    def _process_queue(self):
        """Processes pending UI updates from the queue"""
        try:
            while True:
                msg_type, data = self.update_queue.get_nowait()
                if msg_type == 'video':
                    self._update_video_internal(data)
                elif msg_type == 'stats':
                    self._update_stats_internal(*data)
                elif msg_type == 'status':
                    self.status_lbl.config(text=f"Status: {data}")
        except Empty:
            pass
        finally:
            self.root.after(30, self._process_queue)

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Frames
        style.configure("Main.TFrame", background=cfg.COLOR_BG)
        style.configure("Control.TFrame", background=cfg.COLOR_WHITE)
        
        # Configure Labels
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), background=cfg.COLOR_BG, foreground=cfg.COLOR_PRIMARY)
        style.configure("SubHeader.TLabel", font=("Segoe UI", 12, "bold"), background=cfg.COLOR_WHITE, foreground=cfg.COLOR_PRIMARY)
        style.configure("Normal.TLabel", font=("Segoe UI", 10), background=cfg.COLOR_WHITE, foreground=cfg.COLOR_TEXT)
        style.configure("Status.TLabel", font=("Segoe UI", 9, "italic"), background=cfg.COLOR_WHITE)

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root, style="Main.TFrame")
        header_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Label(header_frame, text="Eye Tracking Control Center", style="Header.TLabel").pack(side='left')
        
        # Main Layout: Left (Controls), Right (Video Feed)
        content_frame = ttk.Frame(self.root, style="Main.TFrame")
        content_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left Panel (Controls)
        left_panel = tk.Frame(content_frame, bg=cfg.COLOR_WHITE, width=320, relief='flat')
        left_panel.pack(side='left', fill='y', padx=(0, 20))
        left_panel.pack_propagate(False)
        
        self.build_user_section(left_panel)
        self.build_control_section(left_panel)
        self.build_settings_section(left_panel)
        self.build_status_section(left_panel)
        
        # Right Panel (Video)
        right_panel = ttk.Frame(content_frame, style="Main.TFrame")
        right_panel.pack(side='left', fill='both', expand=True)
        
        self.video_label = tk.Label(right_panel, bg='black')
        self.video_label.pack(fill='both', expand=True)
        
        # Footer
        footer = tk.Label(self.root, text="Developed by Antigravity AI", bg=cfg.COLOR_BG, fg="#7f8c8d", font=("Segoe UI", 8))
        footer.pack(side='bottom', pady=5)

    def build_user_section(self, parent):
        frame = tk.Frame(parent, bg=cfg.COLOR_WHITE, pady=10, padx=15)
        frame.pack(fill='x')
        
        ttk.Label(frame, text="User Management", style="SubHeader.TLabel").pack(anchor='w', pady=(0, 10))
        
        self.username_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=self.username_var, font=("Segoe UI", 11), relief='solid', bd=1)
        entry.pack(fill='x', pady=5)
        
        btn_frame = tk.Frame(frame, bg=cfg.COLOR_WHITE)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Load Profile", command=self.on_load_profile, 
                  bg=cfg.COLOR_SECONDARY, fg='white', relief='flat', font=("Segoe UI", 9, "bold")).pack(side='left', expand=True, fill='x', padx=(0, 5))
        tk.Button(btn_frame, text="Create", command=self.on_create_profile, 
                  bg=cfg.COLOR_SUCCESS, fg='white', relief='flat', font=("Segoe UI", 9, "bold")).pack(side='left', expand=True, fill='x')

    def build_control_section(self, parent):
        frame = tk.Frame(parent, bg=cfg.COLOR_WHITE, pady=10, padx=15)
        frame.pack(fill='x')
        
        ttk.Label(frame, text="Engine Controls", style="SubHeader.TLabel").pack(anchor='w', pady=(0, 10))
        
        self.start_btn = tk.Button(frame, text="START TRACKING", command=self.on_start, 
                                 bg=cfg.COLOR_SUCCESS, fg='white', relief='flat', font=("Segoe UI", 11, "bold"), pady=10)
        self.start_btn.pack(fill='x', pady=5)
        
        self.stop_btn = tk.Button(frame, text="STOP TRACKING", command=self.on_stop, state='disabled',
                                bg=cfg.COLOR_DANGER, fg='white', relief='flat', font=("Segoe UI", 11, "bold"), pady=10)
        self.stop_btn.pack(fill='x', pady=5)
        
        self.calib_btn = tk.Button(frame, text="CALIBRATION", command=self.on_calibrate,
                                 bg=cfg.COLOR_WARNING, fg='white', relief='flat', font=("Segoe UI", 10, "bold"), pady=5)
        self.calib_btn.pack(fill='x', pady=5)

    def build_settings_section(self, parent):
        frame = tk.Frame(parent, bg=cfg.COLOR_WHITE, pady=10, padx=15)
        frame.pack(fill='x')
        
        ttk.Label(frame, text="Settings", style="SubHeader.TLabel").pack(anchor='w', pady=(0, 5))
        
        # Click Mode
        self.click_mode_var = tk.StringVar(value='blink')
        ttk.Label(frame, text="Click Mode:", style="Normal.TLabel").pack(anchor='w')
        modes_frame = tk.Frame(frame, bg=cfg.COLOR_WHITE)
        modes_frame.pack(fill='x')
        tk.Radiobutton(modes_frame, text="Blink", variable=self.click_mode_var, value='blink', bg=cfg.COLOR_WHITE).pack(side='left')
        tk.Radiobutton(modes_frame, text="Dwell", variable=self.click_mode_var, value='dwell', bg=cfg.COLOR_WHITE).pack(side='left', padx=10)
        
        # Smoothing
        ttk.Label(frame, text="Smoothing:", style="Normal.TLabel").pack(anchor='w', pady=(5, 0))
        self.smooth_scale = ttk.Scale(frame, from_=0.1, to=0.9, orient='horizontal')
        self.smooth_scale.set(cfg.CURSOR_SMOOTHING_DEFAULT)
        self.smooth_scale.pack(fill='x')
        
        tk.Button(frame, text="Save Settings", command=self.on_save_settings,
                  bg=cfg.COLOR_PRIMARY, fg='white', relief='flat', font=("Segoe UI", 9)).pack(fill='x', pady=10)

    def build_status_section(self, parent):
        frame = tk.Frame(parent, bg=cfg.COLOR_WHITE, pady=10, padx=15)
        frame.pack(fill='x', side='bottom')
        
        # dlib Status
        self.dlib_lbl = ttk.Label(frame, text="DLIB: Not Loaded", style="Status.TLabel")
        self.dlib_lbl.pack(anchor='w')
        
        # Progress bar for download
        self.progress = ttk.Progressbar(frame, orient='horizontal', length=200, mode='determinate')
        
        self.download_btn = tk.Button(frame, text="Download DLIB (Advanced Tracking)", 
                                    command=self.on_download_dlib,
                                    bg=cfg.COLOR_SECONDARY, fg='white', relief='flat', font=("Segoe UI", 8))
        if not self.controller.detector.dlib_available:
            self.download_btn.pack(fill='x', pady=5)

        self.user_lbl = ttk.Label(frame, text="User: None", style="Status.TLabel")
        self.user_lbl.pack(anchor='w')
        
        self.fps_lbl = ttk.Label(frame, text="FPS: 0", style="Status.TLabel")
        self.fps_lbl.pack(anchor='w')
        
        self.status_lbl = ttk.Label(frame, text="Status: Ready", style="Status.TLabel")
        self.status_lbl.pack(anchor='w')

    # Event Handlers
    def on_download_dlib(self):
        self.download_btn.pack_forget()
        self.progress.pack(fill='x', pady=5)
        self.status_lbl.config(text="Status: Downloading AI model...")
        
        def update_progress(val):
            # This is called from a thread, so use self.update_queue for label or just risk it for progress bar
            if val >= 100:
                self.root.after(0, lambda: [
                    self.progress.pack_forget(),
                    self.dlib_lbl.config(text="DLIB: Loaded", foreground=cfg.COLOR_SUCCESS),
                    self.status_lbl.config(text="Status: Model ready!")
                ])
            else:
                self.root.after(0, lambda: self.progress.configure(value=val))
                
        threading.Thread(target=self.controller.detector.download_dlib_async, 
                         args=(update_progress,), daemon=True).start()

    def on_load_profile(self):
        username = self.username_var.get()
        if self.controller.load_profile(username):
            self.user_lbl.config(text=f"User: {username}")
            messagebox.showinfo("Success", f"Profile '{username}' loaded.")
        else:
            messagebox.showerror("Error", "Profile not found.")

    def on_create_profile(self):
        username = self.username_var.get()
        if self.controller.create_profile(username):
            messagebox.showinfo("Success", f"Profile '{username}' created.")
        else:
            messagebox.showerror("Error", "Username already exists or invalid.")

    def on_start(self):
        if self.controller.start_tracking():
            self.start_btn.config(state='disabled')
            self.stop_btn.config(state='normal')
            self.status_lbl.config(text="Status: Tracking...", foreground=cfg.COLOR_SUCCESS)

    def on_stop(self):
        self.controller.stop_tracking()
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_lbl.config(text="Status: Stopped", foreground=cfg.COLOR_DANGER)

    def on_calibrate(self):
        # Run calibration in thread
        self.status_lbl.config(text="Status: Calibrating...")
        threading.Thread(target=self.controller.run_calibration, daemon=True).start()

    def on_save_settings(self):
        prefs = {
            'click_mode': self.click_mode_var.get(),
            'cursor_smoothing': self.smooth_scale.get(),
            'scroll_speed': cfg.SCROLL_SPEED_DEFAULT,
            'ear_threshold': cfg.EAR_THRESHOLD_DEFAULT
        }
        self.controller.update_preferences(prefs)
        messagebox.showinfo("Saved", "Settings updated successfully.")

    def update_video(self, frame):
        """Thread-safe request to update video feed"""
        if frame is not None:
            self.update_queue.put(('video', frame.copy()))

    def _update_video_internal(self, frame):
        """Actual video update (must be called from main thread)"""
        # Get parent frame size
        canvas_w = self.video_label.winfo_width()
        canvas_h = self.video_label.winfo_height()
        
        if canvas_w > 1 and canvas_h > 1:
            # Maintain aspect ratio
            img_h, img_w = frame.shape[:2]
            ratio = min(canvas_w/img_w, canvas_h/img_h)
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)
            
            frame = cv2.resize(frame, (new_w, new_h))
            
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(img)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.configure(image=imgtk)

    def update_stats(self, fps, status=None):
        """Thread-safe request to update stats"""
        self.update_queue.put(('stats', (fps, status)))

    def _update_stats_internal(self, fps, status=None):
        self.fps_lbl.config(text=f"FPS: {fps:.1f}")
        if status:
            self.status_lbl.config(text=f"Status: {status}")

    def run(self):
        self.root.mainloop()
