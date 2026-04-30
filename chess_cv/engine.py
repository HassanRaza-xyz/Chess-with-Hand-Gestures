"""
Upgraded Chess Engine using Minimax with Alpha-Beta Pruning.
"""
import chess
import random
import time

class ChessEngine:
    def __init__(self, depth=3, think_time=1.5):
        self.depth = depth
        self.think_time = think_time # Real player jaisa wait time
        # Standard piece values for evaluation
        self.piece_values = {
            chess.PAWN: 10,
            chess.KNIGHT: 30,
            chess.BISHOP: 30,
            chess.ROOK: 50,
            chess.QUEEN: 90,
            chess.KING: 900
        }

    def choose_move(self, board):
        # 1. Thoda wait karein taake natural lagay
        time.sleep(self.think_time)

        # 2. Minimax se best move dhoondein
        best_move = None
        is_white = board.turn == chess.WHITE
        best_value = -99999 if is_white else 99999

        for move in board.legal_moves:
            board.push(move)
            # Agli baari opponent ki hogi, isliye 'not is_white' pass kiya
            board_value = self.minimax(board, self.depth - 1, -100000, 100000, not is_white)
            board.pop()

            if is_white:
                if board_value > best_value:
                    best_value = board_value
                    best_move = move
            else:
                if board_value < best_value:
                    best_value = board_value
                    best_move = move

        # Agar kisi wajah se move na mile, toh random chal de
        if best_move is None:
            best_move = random.choice(list(board.legal_moves))

        return best_move

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        # Agar aakhri depth aagayi ya game khatam, toh score batao
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board)

        if is_maximizing:
            max_eval = -99999
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break # Alpha-Beta Pruning (fazool branches ko cut karna)
            return max_eval
        else:
            min_eval = 99999
            for move in board.legal_moves:
                board.push(move)
                eval = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break # Alpha-Beta Pruning
            return min_eval

    def evaluate_board(self, board):
        # Game over conditions ko handle karna
        if board.is_checkmate():
            if board.turn == chess.WHITE:
                return -9999 # Black ki jeet
            else:
                return 9999  # White ki jeet
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0 # Draw ho gaya

        # Poore board par mojud pieces ka score calculate karna
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        return score