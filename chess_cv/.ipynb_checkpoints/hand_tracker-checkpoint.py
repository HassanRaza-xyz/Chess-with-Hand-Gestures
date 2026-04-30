"""
Pro-Level Hand tracking using MediaPipe (Video Mode for 0 Lag).
"""
import numpy as np
import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision.hand_landmarker import HandLandmarker
from mediapipe.tasks.python.vision.core.image import Image, ImageFormat
import time

class HandTracker:
    def __init__(self):
        # MediaPipe ki advanced configuration setup
        BaseOptions = mp.tasks.BaseOptions
        HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
        VisionRunningMode = mp.tasks.vision.RunningMode

        # OP Configuration: Video mode makes tracking buttery smooth
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path="hand_landmarker.task"),
            running_mode=VisionRunningMode.VIDEO, # <-- THE REAL GAME CHANGER
            num_hands=1,
            min_hand_detection_confidence=0.6,    # False positives filter karna
            min_hand_presence_confidence=0.6,     # Tracking ko lock rakhna
            min_tracking_confidence=0.6           # Jitter (hilna) khatam karna
        )
        
        self.detector = HandLandmarker.create_from_options(options)

    def process(self, frame):
        # Frame ko RGB mein convert karna
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = Image(image_format=ImageFormat.SRGB, data=rgb)
        
        # Video mode ke liye current time (ms) dena zaroori hai
        timestamp_ms = int(time.time() * 1000)
        
        # Detect for video (Memory aur CPU friendly)
        result = self.detector.detect_for_video(mp_image, timestamp_ms)
        
        if result.hand_landmarks and len(result.hand_landmarks) > 0:
            # Sirf pehle haath (hand[0]) ke points aur uski details return karo
            return result.hand_landmarks[0], result.handedness[0]
        
        return None, None

    def get_index_fingertip(self, hand_landmarks, frame_shape):
        if hand_landmarks is None:
            return None
        h, w, _ = frame_shape
        lm = hand_landmarks[8] # 8 is the index finger tip
        x, y = int(lm.x * w), int(lm.y * h)
        return (x, y)