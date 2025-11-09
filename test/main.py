# -*- coding: utf-8 -*-
import os
import sys

import pyaudio
from PySide6 import QtWidgets, QtGui
################################################################################
## Form generated from reading UI file 'main.ui'
##
## Created by: Qt User Interface Compiler version 6.5.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QPushButton, QRadioButton,
                               QSizePolicy, QTextBrowser, QVBoxLayout, QWidget, QButtonGroup, QMessageBox)
from websocket import create_connection

from asr_widget import ASRWidget


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_name = "会议记录小助手"

        self.resize(733, 648)
        self.setWindowTitle(self.app_name)
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName(u"central_widget")
        self.verticalLayout = QVBoxLayout(self.central_widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.main_widget_1 = QWidget(self.central_widget)
        self.main_widget_1.setObjectName(u"main_widget_1")

        self.verticalLayout.addWidget(self.main_widget_1)

        self.main_frame_2 = QFrame(self.central_widget)
        self.main_frame_2.setObjectName(u"main_frame_2")
        font = QFont()
        font.setPointSize(10)
        self.main_frame_2.setFont(font)
        self.main_widget_2_layout = QHBoxLayout(self.main_frame_2)
        self.main_widget_2_layout.setObjectName(u"main_widget_2_layout")
        self.main_widget_2_layout.setContentsMargins(0, 0, 0, 0)
        self.widget_file_select_left = QWidget(self.main_frame_2)
        self.widget_file_select_left.setObjectName(u"widget_file_select_left")

        self.main_widget_2_layout.addWidget(self.widget_file_select_left)

        self.path_text_input = QLineEdit(self.main_frame_2)
        self.path_text_input.setObjectName(u"path_text_input")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.path_text_input.sizePolicy().hasHeightForWidth())
        self.path_text_input.setSizePolicy(sizePolicy)
        self.path_text_input.setMinimumSize(QSize(0, 24))
        self.path_text_input.setMaximumSize(QSize(16777215, 24))
        self.path_text_input.setBaseSize(QSize(0, 0))
        self.path_text_input.setText(u"")

        self.main_widget_2_layout.addWidget(self.path_text_input)

        self.file_select_button = QPushButton(self.main_frame_2)
        self.file_select_button.setObjectName(u"file_select_button")
        self.file_select_button.setMinimumSize(QSize(64, 26))
        self.file_select_button.setMaximumSize(QSize(64, 26))
        self.file_select_button.setText(u"选择文件")

        self.main_widget_2_layout.addWidget(self.file_select_button)

        self.widget_file_select_right = QWidget(self.main_frame_2)
        self.widget_file_select_right.setObjectName(u"widget_file_select_right")

        self.main_widget_2_layout.addWidget(self.widget_file_select_right)

        self.main_widget_2_layout.setStretch(0, 2)
        self.main_widget_2_layout.setStretch(1, 9)
        self.main_widget_2_layout.setStretch(2, 1)
        self.main_widget_2_layout.setStretch(3, 2)

        self.verticalLayout.addWidget(self.main_frame_2)

        self.main_widget_3 = QWidget(self.central_widget)
        self.main_widget_3.setObjectName(u"main_widget_3")
        self.main_widget_3.setFont(font)
        self.main_widget_3_layout = QHBoxLayout(self.main_widget_3)
        self.main_widget_3_layout.setSpacing(0)
        self.main_widget_3_layout.setObjectName(u"main_widget_3_layout")
        self.main_widget_3_layout.setContentsMargins(0, 0, 0, 0)
        self.show_related_frame_right = QFrame(self.main_widget_3)
        self.show_related_frame_right.setObjectName(u"show_related_frame_right")

        self.main_widget_3_layout.addWidget(self.show_related_frame_right)

        self.button_group = QButtonGroup(self)
        self.show_related_group_box = QFrame(self.main_widget_3)
        self.show_related_group_box.setObjectName(u"show_related_group_box")
        self.show_related_group_box_layout = QHBoxLayout(self.show_related_group_box)
        self.show_related_group_box_layout.setSpacing(0)
        self.show_related_group_box_layout.setObjectName(u"show_related_group_box_layout")
        self.show_related_group_box_layout.setContentsMargins(0, 0, 0, 0)
        self.show_related_radio_frame1 = QFrame(self.show_related_group_box)
        self.show_related_radio_frame1.setObjectName(u"show_related_radio_frame1")
        self.show_related_radio_widget1_layout = QHBoxLayout(self.show_related_radio_frame1)
        self.show_related_radio_widget1_layout.setSpacing(0)
        self.show_related_radio_widget1_layout.setObjectName(u"show_related_radio_widget1_layout")
        self.show_related_radio_widget1_layout.setContentsMargins(0, 0, 0, 0)
        self.show_related_radio_button1 = QRadioButton(self.show_related_radio_frame1)
        self.show_related_radio_button1.setObjectName(u"show_related_radio_button1")
        sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.show_related_radio_button1.sizePolicy().hasHeightForWidth())
        self.show_related_radio_button1.setSizePolicy(sizePolicy1)
        self.show_related_radio_button1.setText(u"不显示字幕")
        # if QT_CONFIG(shortcut)
        self.show_related_radio_button1.setShortcut(u"")
        # endif // QT_CONFIG(shortcut)
        self.show_related_radio_button1.setChecked(True)

        self.show_related_radio_widget1_layout.addWidget(self.show_related_radio_button1)

        self.show_related_group_box_layout.addWidget(self.show_related_radio_frame1)

        self.show_related_radio_frame2 = QFrame(self.show_related_group_box)
        self.show_related_radio_frame2.setObjectName(u"show_related_radio_frame2")
        self.show_related_radio_widget2_layout = QHBoxLayout(self.show_related_radio_frame2)
        self.show_related_radio_widget2_layout.setSpacing(0)
        self.show_related_radio_widget2_layout.setObjectName(u"show_related_radio_widget2_layout")
        self.show_related_radio_widget2_layout.setContentsMargins(0, 0, 0, 0)
        self.show_related_radio_button2 = QRadioButton(self.show_related_radio_frame2)
        self.show_related_radio_button2.setObjectName(u"show_related_radio_button2")
        sizePolicy1.setHeightForWidth(self.show_related_radio_button2.sizePolicy().hasHeightForWidth())
        self.show_related_radio_button2.setSizePolicy(sizePolicy1)
        self.show_related_radio_button2.setText(u"显示字幕")
        # if QT_CONFIG(shortcut)
        self.show_related_radio_button2.setShortcut(u"")
        # endif // QT_CONFIG(shortcut)

        self.show_related_radio_widget2_layout.addWidget(self.show_related_radio_button2)

        self.show_related_group_box_layout.addWidget(self.show_related_radio_frame2)

        self.show_related_radio_frame3 = QFrame(self.show_related_group_box)
        self.show_related_radio_frame3.setObjectName(u"show_related_radio_frame3")
        self.show_related_radio_widget3_layout = QHBoxLayout(self.show_related_radio_frame3)
        self.show_related_radio_widget3_layout.setSpacing(0)
        self.show_related_radio_widget3_layout.setObjectName(u"show_related_radio_widget3_layout")
        self.show_related_radio_widget3_layout.setContentsMargins(0, 0, 0, 0)
        self.show_related_radio_button3 = QRadioButton(self.show_related_radio_frame3)
        self.show_related_radio_button3.setObjectName(u"show_related_radio_button3")
        sizePolicy1.setHeightForWidth(self.show_related_radio_button3.sizePolicy().hasHeightForWidth())
        self.show_related_radio_button3.setSizePolicy(sizePolicy1)
        self.show_related_radio_button3.setText(u"显示展板")
        # if QT_CONFIG(shortcut)
        self.show_related_radio_button3.setShortcut(u"")
        # endif // QT_CONFIG(shortcut)

        self.show_related_radio_widget3_layout.addWidget(self.show_related_radio_button3)

        self.button_group.addButton(self.show_related_radio_button1)
        self.button_group.addButton(self.show_related_radio_button2)
        self.button_group.addButton(self.show_related_radio_button3)

        self.show_related_group_box_layout.addWidget(self.show_related_radio_frame3)

        self.main_widget_3_layout.addWidget(self.show_related_group_box)

        self.show_related_frame_left = QFrame(self.main_widget_3)
        self.show_related_frame_left.setObjectName(u"show_related_frame_left")

        self.main_widget_3_layout.addWidget(self.show_related_frame_left)

        self.main_widget_3_layout.setStretch(0, 1)
        self.main_widget_3_layout.setStretch(1, 2)
        self.main_widget_3_layout.setStretch(2, 1)

        self.verticalLayout.addWidget(self.main_widget_3)

        self.main_widget_4 = QWidget(self.central_widget)
        self.main_widget_4.setObjectName(u"main_widget_4")
        self.main_widget_4.setFont(font)
        self.main_widget_4_layout = QHBoxLayout(self.main_widget_4)
        self.main_widget_4_layout.setSpacing(0)
        self.main_widget_4_layout.setObjectName(u"main_widget_4_layout")
        self.main_widget_4_layout.setContentsMargins(0, 0, 0, 0)
        self.asr_button = QPushButton(self.main_widget_4)
        self.asr_button.setObjectName(u"asr_button")
        self.asr_button.setText(u"启动")
        self.asr_button.setMinimumSize(QSize(100, 40))
        self.asr_button.setMaximumSize(QSize(100, 40))

        self.main_widget_4_layout.addWidget(self.asr_button)

        self.verticalLayout.addWidget(self.main_widget_4)

        self.main_widget_5 = QWidget(self.central_widget)
        self.main_widget_5.setObjectName(u"main_widget_5")
        font1 = QFont()
        font1.setPointSize(16)
        self.main_widget_5.setFont(font1)
        self.main_widget_5_layout = QHBoxLayout(self.main_widget_5)
        self.main_widget_5_layout.setSpacing(0)
        self.main_widget_5_layout.setObjectName(u"main_widget_5_layout")
        self.main_widget_5_layout.setContentsMargins(0, 5, 0, 0)
        self.show_text_browser = QTextBrowser(self.main_widget_5)
        self.show_text_browser.setObjectName(u"show_text_browser")
        self.show_text_browser.setFrameShape(QFrame.NoFrame)
        self.show_text_browser.setMarkdown(u"")
        self.show_text_browser.setText(u"")
        self.show_text_browser.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)
        self.show_text_browser.setPlaceholderText(u"")

        self.main_widget_5_layout.addWidget(self.show_text_browser)

        self.verticalLayout.addWidget(self.main_widget_5)

        self.main_widget_6 = QWidget(self.central_widget)
        self.main_widget_6.setObjectName(u"main_widget_6")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.main_widget_6.sizePolicy().hasHeightForWidth())
        self.main_widget_6.setSizePolicy(sizePolicy2)
        self.main_widget_6.setMinimumSize(QSize(0, 40))
        self.main_widget_6.setMaximumSize(QSize(16777215, 40))
        font2 = QFont()
        font2.setPointSize(8)
        self.main_widget_6.setFont(font2)
        self.main_widget_6_layout = QVBoxLayout(self.main_widget_6)
        self.main_widget_6_layout.setSpacing(0)
        self.main_widget_6_layout.setObjectName(u"main_widget_6_layout")
        self.main_widget_6_layout.setContentsMargins(8, 0, 8, 8)
        self.copyright_text_label = QLabel(self.main_widget_6)
        self.copyright_text_label.setObjectName(u"copyright_text_label")
        self.copyright_text_label.setText(u"meeting minutes software by wzifan, version: 4.0 (closed beta version)")
        sizePolicy3 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.copyright_text_label.sizePolicy().hasHeightForWidth())
        self.copyright_text_label.setSizePolicy(sizePolicy3)
        self.copyright_text_label.setMinimumSize(QSize(0, 0))
        self.copyright_text_label.setMaximumSize(QSize(16777215, 16777215))
        self.copyright_text_label.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.main_widget_6_layout.addWidget(self.copyright_text_label)

        self.verticalLayout.addWidget(self.main_widget_6)

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 3)
        self.verticalLayout.setStretch(2, 3)
        self.verticalLayout.setStretch(3, 3)
        self.verticalLayout.setStretch(4, 15)
        self.verticalLayout.setStretch(5, 1)
        self.setCentralWidget(self.central_widget)

        QMetaObject.connectSlotsByName(self)

    def asr_widget_control(self):
        if not self.asr_widget_started:
            self.asr_button.setDisabled(True)
            self.asr_button.setText("正在启动")
            self.asr_button.repaint()
            input_path = self.path_text_input.text()
            if input_path != '':
                if os.path.basename(input_path) != '':
                    self.text_save_path = input_path
                else:
                    self.text_save_path = os.path.join(os.path.dirname(input_path), "asr_result.txt")
            else:
                self.text_save_path = os.path.abspath(os.path.join(self.home_dir, 'Documents/asr_result.txt'))
            self.path_text_input.setText(self.text_save_path)
            self.path_text_input.repaint()
            text_save_dir = os.path.dirname(self.text_save_path)
            if not os.path.isdir(text_save_dir):
                os.makedirs(text_save_dir)
            # get device info
            p = pyaudio.PyAudio()
            try:
                device_info = p.get_default_input_device_info()
                device_id = int(device_info['index'])
                channels = int(device_info['maxInputChannels'])
                record_rate = int(device_info['defaultSampleRate'])
                stream = p.open(format=pyaudio.paInt16,
                                channels=channels,
                                rate=record_rate,
                                input=True,
                                input_device_index=device_id,
                                frames_per_buffer=1024)
            except:
                QMessageBox.critical(self, "警告", "请接入麦克风或音频输入设备，\n并重新启动程序！")
                self.asr_button.setText("启动")
                self.asr_widget_started = False
                self.asr_button.setDisabled(False)
                return
            finally:
                p.terminate()
            # test connection
            ws_url = f"wss://{self.server_addr}:{self.server_port}"
            ws = None
            try:
                ws = create_connection(ws_url, sslopt={"cert_reqs": ssl.CERT_NONE})
            except:
                QMessageBox.critical(self, "错误", "网络连接异常！")
                self.asr_button.setText("启动")
                self.asr_widget_started = False
                self.asr_button.setDisabled(False)
                return
            finally:
                if ws is not None:
                    ws.close()

            self.asr_widget = ASRWidget(server_addr=self.server_addr, server_port=self.server_port,
                                        text_save_path=self.text_save_path, device_id=device_id)
            # signal connect
            self.asr_widget.button_signal.connect(self.button_close)
            self.asr_widget.streaming_asr_thread.asr_record_text_signal.connect(self.set_asr_text_in_main_window)
            if self.show_text_ratio_button2.isChecked():
                self.asr_widget.show()
            self.asr_button.setText("关闭")
            self.asr_widget_started = True
            self.asr_button.setDisabled(False)
        else:
            if self.asr_widget is not None:
                self.asr_widget.close()

    def button_close(self, closed: bool = False):
        if not closed:
            self.asr_button.setDisabled(True)
            self.asr_button.setText("正在关闭")
            self.asr_button.repaint()
            self.show_text_main_window.setText("")
        else:
            self.asr_button.setText("启动")
            self.asr_widget_started = False
            self.asr_button.setDisabled(False)

    def select_path(self):
        file_path, file_type = QFileDialog.getOpenFileName(self, "选择识别文本存放的文件")
        if file_path != "":
            self.path_text_input.setText(os.path.abspath(file_path))

    def set_asr_text_in_main_window(self, asr_text_result):
        self.show_text_main_window.setText(asr_text_result)

    def closeEvent(self, event):
        if self.asr_widget is not None:
            self.asr_widget.close()


# 程序入口
if __name__ == "__main__":
    # 初始化QApplication，界面展示要包含在QApplication初始化之后，结束之前
    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    icon = QtGui.QIcon("icons/icon.png")
    app.setWindowIcon(icon)

    # 初始化并展示我们的界面组件
    window = Ui_MainWindow()
    window.show()

    # 结束QApplication
    sys.exit(app.exec())
