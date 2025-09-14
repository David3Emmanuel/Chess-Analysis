import sys
from PyQt5 import QtWidgets, QtSvg, QtCore
from typing import Callable, Optional
from matplotlib import pyplot as plt

app = QtWidgets.QApplication.instance()
if app is None:
    app = QtWidgets.QApplication(sys.argv)

svg_widget = QtSvg.QSvgWidget()
svg_widget.setWindowTitle("Chess Board")
svg_widget.resize(400, 400)
svg_widget.show()

window_closed = False

def close_event(a0: Optional[QtCore.QEvent]) -> None:
    global window_closed
    if a0:
        window_closed = True
        a0.accept()
svg_widget.closeEvent = close_event

def is_closed() -> bool:
    return window_closed

def display_svg(svg: str) -> None:
    svg_widget.load(QtCore.QByteArray(svg.encode()))
    svg_widget.update()
    if app:
        app.processEvents()

def finish_display() -> None:
    if app: app.exec_()

def plot_position_history(position_history):
    moves = [entry['move_number'] for entry in position_history]
    material = [entry['analysis'].get('material', 0) for entry in position_history]
    development = [entry['analysis'].get('development', 0) for entry in position_history]
    mobility = [entry['analysis'].get('mobility', 0) for entry in position_history]
    evals = [entry['analysis'].get('eval', 0) for entry in position_history]

    plt.figure(figsize=(12, 6))
    
    plt.plot(moves, material, label='Material', marker='o')
    plt.plot(moves, development, label='Development', marker='o')
    plt.plot(moves, mobility, label='Mobility', marker='o')
    plt.plot(moves, evals, label='Evaluation', marker='o')
    
    plt.title('Position Analysis Over Time')
    plt.xlabel('Move Number')
    plt.ylabel('Evaluation')
    plt.axhline(0, color='black', lw=0.5, ls='--')
    plt.legend()
    plt.grid()
    plt.show()