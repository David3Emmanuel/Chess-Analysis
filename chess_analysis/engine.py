from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import chess
import joblib
import pandas as pd
from stockfish import Stockfish
import numpy as np


class Engine(ABC):
    """Abstract base class for chess engines."""
    
    @abstractmethod
    def set_board(self, board: chess.Board) -> None:
        """Set the board."""
        pass
    
    @abstractmethod
    def get_evaluation(self) -> Dict[str, Any]:
        """Get the evaluation of the current position.
        
        Returns:
            Dict with 'type' ('cp' for centipawns, 'mate' for mate) and 'value'
        """
        pass
    
    @abstractmethod
    def get_best_move(self) -> Optional[str]:
        """Get the best move in UCI format.
        
        Returns:
            UCI move string or None if no move available
        """
        pass


class StockfishEngine(Engine):
    """Stockfish engine implementation."""
    
    def __init__(self, path: str = "stockfish", depth: int = 15):
        """Initialize Stockfish engine.
        
        Args:
            path: Path to stockfish executable
            depth: Search depth for analysis
        """
        self.engine = Stockfish(path=path, depth=depth)

    def set_board(self, board: chess.Board) -> None:
        """Set the board."""
        self.engine.set_fen_position(board.fen())

    def get_evaluation(self) -> Dict[str, Any]:
        """Get the evaluation of the current position.
        
        Returns:
            Dict with 'type' ('cp' for centipawns, 'mate' for mate) and 'value'
        """
        return self.engine.get_evaluation()
    
    def get_best_move(self) -> Optional[str]:
        """Get the best move in UCI format.
        
        Returns:
            UCI move string or None if no move available
        """
        return self.engine.get_best_move()


class CustomModelEngine(Engine):
    """Custom model engine implementation using a joblib-saved model."""
    
    def __init__(self, model_path: str, depth: int = 3):
        """Initialize custom model engine.
        
        Args:
            model_path: Path to the joblib-saved model
            depth: Search depth for move generation (number of moves to consider)
        """
        from .position_analysis import position_analysis_without_eval
        
        self.model = joblib.load(model_path)
        self.depth = depth
        self.board = chess.Board()
        self.analysis = position_analysis_without_eval

    def set_board(self, board: chess.Board) -> None:
        """Set the board."""
        self.board = board

    def get_evaluation(self) -> Dict[str, Any]:
        """Get the evaluation of the current position using the custom model.
        
        Returns:
            Dict with 'type' ('cp' for centipawns) and 'value'
        """
        if self.board.is_game_over():
            result = self.board.result()
            if result == "1-0":
                return {'type': 'cp', 'value': 2000}  # Large positive value for white win
            elif result == "0-1":
                return {'type': 'cp', 'value': -2000}  # Large negative value for black win
            else:
                return {'type': 'cp', 'value': 0}  # Draw

        analysis_result = self.analysis(self.board)
        features_df = pd.DataFrame([analysis_result]).select_dtypes(include=[np.number, bool])
        X = features_df.values

        # Make prediction using the model
        try:
            prediction = self.model.predict(X)[0]
            centipawns = int(prediction * 100)
            return {'type': 'cp', 'value': centipawns}
        except Exception as e:
            # Fallback to neutral evaluation if model prediction fails
            print(f"Model prediction failed: {e}")
            return {'type': 'cp', 'value': 0}
    
    def get_best_move(self) -> Optional[str]:
        """Get the best move using minimax search with the custom model evaluation.
        
        Returns:
            UCI move string or None if no move available
        """
        if self.board.is_game_over():
            return None
        
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return None
        
        best_move = None
        best_score = float('-inf') if self.board.turn == chess.WHITE else float('inf')
        
        for move in legal_moves:
            # Make the move
            self.board.push(move)
            
            # Evaluate the resulting position
            eval_result = self.get_evaluation()
            score = eval_result['value']
            
            # Undo the move
            self.board.pop()
            
            # Update best move based on whose turn it is
            if self.board.turn == chess.WHITE:  # White wants higher scores
                if score > best_score:
                    best_score = score
                    best_move = move
            else:  # Black wants lower scores
                if score < best_score:
                    best_score = score
                    best_move = move
        
        return best_move.uci() if best_move else None