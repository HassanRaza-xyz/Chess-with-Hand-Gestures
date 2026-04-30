"""
Advanced Gesture detection logic for hand chess control. (Fixed & OP Version)
"""
import numpy as np

class GestureController:
    def __init__(self):
        self.prev_pinch = False
        
        # 🛡️ HYSTERESIS ALGORITHM: Pakarne aur chhorne ka margin alag alag
        self.pinch_start_threshold = 0.05  # Pakarne ke liye strict
        self.pinch_drop_threshold = 0.08   # Chhorne ke liye margin thoda zyada

        self.prev_two_finger = False
        self.two_finger_threshold = 0.06
        
        # ⏱️ FRAME BUFFER: Random false-positive restarts rokne ke liye
        self.thumb_up_frames = 0 

    def detect(self, hand_landmarks, frame_shape):
        if hand_landmarks is None:
            self.prev_pinch = False
            self.prev_two_finger = False
            self.thumb_up_frames = 0
            return None
            
        lm = hand_landmarks
        
        # Har ungli ke tips
        thumb_tip = np.array([lm[4].x, lm[4].y])
        index_tip = np.array([lm[8].x, lm[8].y])
        middle_tip = np.array([lm[12].x, lm[12].y])
        ring_tip = np.array([lm[16].x, lm[16].y])
        pinky_tip = np.array([lm[20].x, lm[20].y])
        
        pinch_dist = np.linalg.norm(thumb_tip - index_tip)
        two_finger_dist = np.linalg.norm(index_tip - middle_tip)

        # Ungliyon ka status
        index_closed = index_tip[1] > lm[6].y
        middle_closed = middle_tip[1] > lm[10].y
        ring_closed = ring_tip[1] > lm[14].y
        pinky_closed = pinky_tip[1] > lm[18].y

        # 1. PINCH & DROP (Fixed with Hysteresis 🔥)
        if self.prev_pinch:
            # Agar piece pakra hua hai, toh tab tak mat chhoro jab tak distance bada na ho jaye
            if pinch_dist > self.pinch_drop_threshold:
                self.prev_pinch = False
                return 'release'
        else:
            # Naya piece pakarne ke liye distance chota hona chahiye
            if pinch_dist < self.pinch_start_threshold:
                self.prev_pinch = True
                return 'pinch'

        # 2. TWO-FINGER TAP ✌️
        if two_finger_dist < self.two_finger_threshold and ring_closed and pinky_closed:
            if not self.prev_two_finger:
                self.prev_two_finger = True
                return 'two_finger_tap'
        else:
            self.prev_two_finger = False

        # 3. REAL THUMB UP 👍 (Fixed with Frame Buffer ⏱️)
        if index_closed and middle_closed and ring_closed and pinky_closed:
            if thumb_tip[1] < lm[3].y and np.linalg.norm(thumb_tip - index_tip) > 0.1:
                self.thumb_up_frames += 1
                # 15 frames (approx 0.5s) tak hold karne pe hi trigger hoga!
                if self.thumb_up_frames > 15: 
                    self.thumb_up_frames = 0
                    return 'thumb_up'
                return None
        
        # Agar haath hil gaya ya hold nahi kiya toh counter reset maro
        self.thumb_up_frames = 0
        
        # 4. OPEN PALM ✋
        if not index_closed and not middle_closed and not ring_closed and not pinky_closed:
            if pinch_dist > 0.1:
                return 'open_palm'

        return None