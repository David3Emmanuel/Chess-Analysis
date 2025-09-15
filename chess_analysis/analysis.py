from typing import Any, Callable, Optional
import chess
from .engine import Engine, StockfishEngine

class Analysis:
    def __init__(self, engine: Optional[Engine] = None):
        self.pipeline = []
        
        if engine is None:
            engine = StockfishEngine(path="stockfish", depth=15)
        self.engine = engine
        
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

    def copy(self) -> 'Analysis':
        return self.copy_with_engine(self.engine)

    def copy_with_engine(self, engine: Engine) -> 'Analysis':
        new_analysis = Analysis(engine)
        new_analysis.pipeline = self.pipeline.copy()
        new_analysis.persist = self.persist.copy()
        new_analysis.context = self.context.copy()
        return new_analysis
