import cv2
import time
import threading
import numpy as np
from typing import Optional, Tuple
from backend.ai.stream.synthetic_source import SyntheticCameraSource
from backend.utils.logger import logger

class CameraSource:
    """
    Unified Camera Source Abstraction supporting:
    - RTSP: Real-time IP camera streams
    - VIDEO_FILE: Looping MP4/AVI files for evaluation
    - WEBCAM: Direct hardware camera capture
    - DEMO: Realistic synthetic simulated camera stream
    """
    def __init__(
        self,
        camera_id: int,
        camera_code: str,
        name: str,
        location: str,
        source_type: str = "DEMO",
        rtsp_url: Optional[str] = None,
        video_file_path: Optional[str] = None,
        fps: float = 10.0
    ):
        self.camera_id = camera_id
        self.camera_code = camera_code
        self.name = name
        self.location = location
        self.source_type = source_type.upper()
        self.rtsp_url = rtsp_url
        self.video_file_path = video_file_path
        self.target_fps = fps
        self.is_running = False
        self.cap: Optional[cv2.VideoCapture] = None
        self.synthetic_source: Optional[SyntheticCameraSource] = None
        
        self.latest_frame: Optional[np.ndarray] = None
        self.lock = threading.Lock()
        self.worker_thread: Optional[threading.Thread] = None
        self.last_frame_time = time.time()
        self.actual_fps = 0.0
        self.frame_count = 0
        self.error_message: Optional[str] = None

    def start(self):
        if self.is_running:
            return
        self.is_running = True

        if self.source_type == "DEMO":
            self.synthetic_source = SyntheticCameraSource(
                camera_code=self.camera_code,
                name=self.name,
                location=self.location,
                fps=self.target_fps
            )
            logger.info(f"Initialized Synthetic Stream for {self.camera_code}")
        elif self.source_type == "VIDEO_FILE" and self.video_file_path:
            self.cap = cv2.VideoCapture(self.video_file_path)
            logger.info(f"Initialized Video File Stream for {self.camera_code}: {self.video_file_path}")
        elif self.source_type == "RTSP" and self.rtsp_url:
            self.cap = cv2.VideoCapture(self.rtsp_url)
            logger.info(f"Initialized RTSP Stream for {self.camera_code}: {self.rtsp_url}")
        elif self.source_type == "WEBCAM":
            self.cap = cv2.VideoCapture(0)
            logger.info(f"Initialized Webcam Stream for {self.camera_code}")
        else:
            # Fallback to demo mode if specific source is unavailable
            self.source_type = "DEMO"
            self.synthetic_source = SyntheticCameraSource(
                camera_code=self.camera_code,
                name=self.name,
                location=self.location,
                fps=self.target_fps
            )
            logger.warning(f"No valid source found for {self.camera_code}. Defaulted to Demo stream.")

        self.worker_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.worker_thread.start()

    def _capture_loop(self):
        fps_timer = time.time()
        frames_in_second = 0

        while self.is_running:
            frame = None
            success = False

            if self.source_type == "DEMO" and self.synthetic_source:
                success, frame = self.synthetic_source.read()
            elif self.cap and self.cap.isOpened():
                success, frame = self.cap.read()
                if not success and self.source_type == "VIDEO_FILE":
                    # Loop video file for continuous playback
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    success, frame = self.cap.read()
            
            if not success or frame is None:
                # Generate placeholder frame
                frame = self._generate_offline_frame()

            with self.lock:
                self.latest_frame = frame
                self.last_frame_time = time.time()
                self.frame_count += 1
                frames_in_second += 1

            now = time.time()
            if now - fps_timer >= 1.0:
                self.actual_fps = frames_in_second / (now - fps_timer)
                frames_in_second = 0
                fps_timer = now

            # Throttle if reading from real capture
            time.sleep(max(0.01, 1.0 / max(1.0, self.target_fps)))

    def _generate_offline_frame(self) -> np.ndarray:
        frame = np.zeros((360, 640, 3), dtype=np.uint8)
        frame[:] = (30, 20, 20)
        cv2.putText(frame, f"{self.camera_code} - CAMERA SOURCE OFFLINE", (110, 160),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
        cv2.putText(frame, "Check RTSP URL or Source Configuration", (160, 200),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)
        return frame

    def read_frame(self) -> Tuple[bool, Optional[np.ndarray]]:
        with self.lock:
            if self.latest_frame is not None:
                return True, self.latest_frame.copy()
            return False, None

    def get_ground_truth_bbox(self) -> Optional[Tuple[int, int, int, int]]:
        if self.synthetic_source and hasattr(self.synthetic_source, "current_person_bbox"):
            return self.synthetic_source.current_person_bbox
        return None

    def stop(self):
        self.is_running = False
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
        logger.info(f"Stopped stream for {self.camera_code}")
