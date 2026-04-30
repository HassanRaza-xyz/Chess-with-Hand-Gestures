"""
Optimized Chessboard UI rendering and coordinate mapping.
"""

import numpy as np
import cv2
import chess
import os

class ChessboardUI:
    def __init__(self, board_size=360, margin=25): # Margin thoda badhaya hai text ke liye
        self.board_size = board_size
        self.margin = margin
        self.square_size = (board_size - 2 * margin) // 8
        self.colors = [(222, 202, 163), (139, 108, 66)]  # light, dark (wood style)
        
        # Load aur RESIZE pieces sirf ek dafa memory mein (Massive Performance Boost)
        self.piece_images = self.load_piece_images()

    def load_piece_images(self):
        base = os.path.join(os.path.dirname(__file__), "assets", "wood")
        mapping = {
            (chess.PAWN, True):   "wP.png", (chess.KNIGHT, True): "wN.png",
            (chess.BISHOP, True): "wB.png", (chess.ROOK, True):   "wR.png",
            (chess.QUEEN, True):  "wQ.png", (chess.KING, True):   "wK.png",
            (chess.PAWN, False):  "bP.png", (chess.KNIGHT, False):"bN.png",
            (chess.BISHOP, False):"bB.png", (chess.ROOK, False):  "bR.png",
            (chess.QUEEN, False): "bQ.png", (chess.KING, False):  "bK.png",
        }
        images = {}
        for key, fname in mapping.items():
            path = os.path.join(base, fname)
            if os.path.exists(path):
                img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
                if img is not None:
                    # Resize image exactly once when loading
                    img = cv2.resize(img, (self.square_size, self.square_size), interpolation=cv2.INTER_AREA)
                    images[key] = img
        return images

    def get_square_from_pos(self, pos):
        if pos is None:
            return None
        x, y = pos
        bx = x - self.margin
        by = y - self.margin
        if bx < 0 or by < 0 or bx >= self.square_size * 8 or by >= self.square_size * 8:
            return None
        file = int(bx // self.square_size)
        rank = int(7 - (by // self.square_size))
        if 0 <= file < 8 and 0 <= rank < 8:
            return chess.square(file, rank)
        return None

    def get_square_center(self, square):
        file = chess.square_file(square)
        rank = chess.square_rank(square)
        x = self.margin + file * self.square_size + self.square_size // 2
        y = self.margin + (7 - rank) * self.square_size + self.square_size // 2
        return (x, y)

    def draw(self, img, board, hover_square=None, selected_square=None, legal_moves=None):
        # 1. Draw squares
        for rank in range(8):
            for file in range(8):
                square = chess.square(file, 7 - rank)
                color = self.colors[(file + rank) % 2]
                x0 = self.margin + file * self.square_size
                y0 = self.margin + rank * self.square_size
                x1 = x0 + self.square_size
                y1 = y0 + self.square_size
                
                cv2.rectangle(img, (x0, y0), (x1, y1), color, -1)
                
                # Highlights
                if legal_moves and square in legal_moves:
                    cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 0), 3)
                if hover_square == square:
                    cv2.rectangle(img, (x0, y0), (x1, y1), (0, 255, 255), 3)
                if selected_square == square:
                    cv2.rectangle(img, (x0, y0), (x1, y1), (0, 128, 255), 4)

        # 2. Draw Board Coordinates (A-H and 1-8)
        font = cv2.FONT_HERSHEY_SIMPLEX
        for i in range(8):
            # Columns (a, b, c...)
            cv2.putText(img, chr(ord('a') + i), (self.margin + i*self.square_size + self.square_size//2 - 5, self.margin + 8*self.square_size + 15), font, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
            # Rows (1, 2, 3...)
            cv2.putText(img, str(8 - i), (self.margin - 18, self.margin + i*self.square_size + self.square_size//2 + 5), font, 0.4, (255, 255, 255), 1, cv2.LINE_AA)

        # 3. Draw pieces cleanly
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                img_piece = self.piece_images.get((piece.piece_type, piece.color))
                if img_piece is not None:
                    x, y = self.get_square_center(square)
                    px0 = x - self.square_size // 2
                    py0 = y - self.square_size // 2
                    self.overlay_png(img, img_piece, px0, py0)
        return img

    def overlay_png(self, bg, fg, x, y):
        # Image bounding logic to prevent OpenCV crash out of bounds
        h, w = fg.shape[:2]
        if y < 0 or y+h > bg.shape[0] or x < 0 or x+w > bg.shape[1]:
            return
            
        if fg.shape[2] == 4:
            alpha = fg[:, :, 3] / 255.0
            for c in range(3):
                bg[y:y+h, x:x+w, c] = (1 - alpha) * bg[y:y+h, x:x+w, c] + alpha * fg[:, :, c]
        else:
            bg[y:y+h, x:x+w] = fg