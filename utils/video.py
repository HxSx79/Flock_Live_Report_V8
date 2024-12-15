"""Module for handling video streams"""
import cv2
import time
from typing import Generator, Optional, Tuple
from werkzeug.datastructures import FileStorage

class VideoStream:
    def __init__(self):
        self.cap = None
        self.test_video = None
        self.last_frame_time = 0
        self.frame_interval = 1.0 / 25  # 25 FPS
        self.target_aspect_ratio = 16 / 9
        self.frame_count = 0
        self.last_frame = None

    def set_test_video(self, video_file: FileStorage) -> None:
        """Set up test video and reset tracking state"""
        try:
            # Save uploaded file
            temp_path = "/tmp/test_video.mp4"
            video_file.save(temp_path)
            
            # Release existing video if any
            if self.test_video is not None:
                self.test_video.release()
            
            # Open new video
            self.test_video = cv2.VideoCapture(temp_path)
            if not self.test_video.isOpened():
                raise ValueError("Failed to open video file")
            
            # Reset state
            self.frame_count = 0
            self.last_frame_time = time.time()
            self.last_frame = None
            
            print("Test video loaded successfully")
            
        except Exception as e:
            print(f"Error setting test video: {e}")
            raise

    def read_frame(self) -> Tuple[bool, Optional[cv2.Mat]]:
        """Read frame with consistent frame rate"""
        current_time = time.time()
        elapsed = current_time - self.last_frame_time
        
        # Maintain frame rate
        if elapsed < self.frame_interval:
            if self.last_frame is not None:
                return True, self.last_frame.copy()
            time.sleep(self.frame_interval - elapsed)
        
        # Read from test video if available
        if self.test_video is not None:
            ret, frame = self.test_video.read()
            if not ret:
                # Loop video
                self.test_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.test_video.read()
                self.frame_count = 0
            
            if ret:
                self.frame_count += 1
                self.last_frame = frame.copy()
                self.last_frame_time = current_time
            return ret, frame
        
        # Fallback to camera
        if self.cap is None:
            self.start_camera()
        
        ret, frame = self.cap.read()
        if ret:
            self.last_frame = frame.copy()
            self.last_frame_time = current_time
        return ret, frame