import sys
from PyQt5 import QtWidgets, QtSvg, QtCore
from typing import Callable, Optional

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