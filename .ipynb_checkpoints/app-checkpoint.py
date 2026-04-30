"""
Advanced Main application logic for Real-Time Hand Gesture Chess
"""
import cv2
import chess
import sys
import threading # AI ko background mein chalane ke liye

from .hand_tracker import HandTracker
from .chessboard import ChessboardUI
from .gesture import GestureController
from .engine import ChessEngine

def main():
    # Initialize modules
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        sys.exit(1)

    hand_tracker = HandTracker()
    chessboard_ui = ChessboardUI()
    gesture_ctrl = GestureController()
    engine = ChessEngine()
    board = chess.Board()

    # Game States
    selected_square = None
    drag_pixel_pos = None
    is_pinching = False
    human_turn = True
    ai_thinking = False
    game_paused = False
    running = True

    # --- THE MAGIC TRICK: AI Threading ---
    def ai_worker():
        nonlocal human_turn, ai_thinking
        move = engine.choose_move(board)
        if move:
            board.push(move)
        human_turn = True
        ai_thinking = False

    cv2.namedWindow("Hand Gesture Chess")
    
    while running:
        ret, frame = cap.read()
        if not ret: break
        
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (960, 720))
        
        # 1. Tracker aur Gesture update
        hand_landmarks, handedness = hand_tracker.process(frame)
        gesture = gesture_ctrl.detect(hand_landmarks, frame.shape)
        
        ix = iy = hover_square = None

        if hand_landmarks:
            ix, iy = hand_tracker.get_index_fingertip(hand_landmarks, frame.shape)
            hover_square = chessboard_ui.get_square_from_pos((ix, iy))

            # --- 2. OP GESTURE CONTROLS (Restart Removed!) ---
            if gesture == 'open_palm':
                game_paused = not game_paused # Pause toggle
                cv2.waitKey(300) # Thoda debounce taake bar bar toggle na ho

            # Agar game chal rahi hai toh moves allow karo
            if not game_paused and human_turn:
                if gesture == 'pinch' and not is_pinching:
                    is_pinching = True
                    if hover_square is not None:
                        piece = board.piece_at(hover_square)
                        if piece and piece.color == chess.WHITE:
                            selected_square = hover_square
                
                elif gesture == 'release' and is_pinching:
                    is_pinching = False
                    if selected_square is not None and hover_square is not None:
                        move = chess.Move(selected_square, hover_square)
                        # Pawn promotion check
                        promo_move = chess.Move(selected_square, hover_square, promotion=chess.QUEEN)
                        
                        if promo_move in board.legal_moves:
                            board.push(promo_move)
                            human_turn = False
                        elif move in board.legal_moves:
                            board.push(move)
                            human_turn = False # Ab computer ki baari
                    selected_square = None

            if is_pinching and ix is not None:
                drag_pixel_pos = (ix, iy)

        # --- 3. BACKGROUND AI TASK ---
        if not human_turn and not ai_thinking and not board.is_game_over():
            ai_thinking = True
            threading.Thread(target=ai_worker).start() # AI sochega bina camera rokay

        # --- 4. CLEAN RENDERING ---
        # Hack: Jab piece uthayein, usko board se hide kar dein taake UI wahan na draw kare
        temp_piece = None
        if is_pinching and selected_square is not None:
            temp_piece = board.piece_at(selected_square)
            board.remove_piece_at(selected_square)

        # Draw main board
        legal_moves_list = [m.to_square for m in board.legal_moves if m.from_square == selected_square] if selected_square else []
        frame = chessboard_ui.draw(frame, board, hover_square, selected_square, legal_moves_list)

        # Piece wapas rakhein aur hawa mein (finger par) draw karein
        if temp_piece is not None:
            board.set_piece_at(selected_square, temp_piece)
            img_piece = chessboard_ui.piece_images.get((temp_piece.piece_type, temp_piece.color))
            if img_piece is not None and drag_pixel_pos:
                sz = chessboard_ui.square_size
                chessboard_ui.overlay_png(frame, img_piece, int(drag_pixel_pos[0] - sz//2), int(drag_pixel_pos[1] - sz//2))

        # Green tracker dot
        if ix is not None and iy is not None:
            cv2.circle(frame, (ix, iy), 10, (0, 255, 0), -1)

        # --- UI TEXTS ---
        if ai_thinking:
            cv2.putText(frame, "AI is thinking...", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)
        if game_paused:
            cv2.putText(frame, "PAUSED (Open Palm to Resume)", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

        if board.is_checkmate():
            winner = "Black" if board.turn == chess.WHITE else "White"
            cv2.putText(frame, f"CHECKMATE! {winner} Wins!", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3, cv2.LINE_AA)
        elif board.is_check():
            cv2.putText(frame, "CHECK!", (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3, cv2.LINE_AA)

        cv2.imshow("Hand Gesture Chess", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            running = False

    cap.release()
    cv2.destroyAllWindows()