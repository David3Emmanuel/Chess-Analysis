from typing import Any, Callable, Optional
import chess
from stockfish import Stockfish

class Analysis:
    def __init__(self):
        self.pipeline = []
        self.engine = Stockfish(path="stockfish", depth=15)
        self.persist = {}
        self.reset()

    def reset(self, board: Optional[chess.Board] = None):
        self.board = board if board else chess.Board()
        self.context = self.persist

    def __getitem__(self, item) -> Any:
        if item in self.context:
            return self.context.get(item)
        else:
            return self.persist.get(item)
    
    def __setitem__(self, key, value):
        self.context[key] = value

    def __or__(self, func: Callable[['Analysis'], Any]) -> 'Analysis':
        self.pipeline.append(func)
        return self
    
    def __call__(self, board: Optional[chess.Board]) -> Any:
        self.reset(board)
        out = None
        for func in self.pipeline:
            out = func(self)
        return out
