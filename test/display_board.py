# -*- coding: utf-8 -*-
from PySide6 import QtGui
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt, Signal)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QMainWindow, QSizePolicy,
                               QTextBrowser, QVBoxLayout, QWidget)


class DisplayBoard(QMainWindow):
    close_signal = Signal()

    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle(u"会议记录小助手")

        self.central_widget = QWidget(self)
        self.central_widget.setObjectName(u"central_widget")
        font = QFont()
        font.setPointSize(64)
        font.setBold(True)
        self.central_widget.setFont(font)
        self.central_widget.setStyleSheet(u"background-color:rgba(0,28,39,1.0);color:rgba(255,255,255,1.0);")
        self.central_widget_layout = QVBoxLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setObjectName(u"central_widget_layout")
        self.central_widget_layout.setContentsMargins(20, 20, 5, 5)
        self.show_text_board = QTextBrowser(self.central_widget)
        self.show_text_board.setObjectName(u"show_text_board")
        self.show_text_board.setFrameShape(QFrame.NoFrame)
        self.show_text_board.setFont(font)

        self.central_widget_layout.addWidget(self.show_text_board)

        self.setCentralWidget(self.central_widget)

        QMetaObject.connectSlotsByName(self)

    def set_display_text(self, asr_text_result):
        self.show_text_board.setText(asr_text_result)
        self.show_text_board.moveCursor(QtGui.QTextCursor.End)

    def closeEvent(self, event):
        self.close_signal.emit()
