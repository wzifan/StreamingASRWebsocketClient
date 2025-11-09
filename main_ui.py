# -*- coding: utf-8 -*-
import os
import ssl
import subprocess
import sys
import time
from ctypes import windll
from threading import Thread
from datetime import datetime

import psutil
import pyaudio
from PySide6 import QtWidgets, QtGui

from PySide6.QtCore import (QMetaObject, QSize, Qt, QThread, Signal)
from PySide6.QtGui import (QFont)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QPushButton, QRadioButton,
                               QSizePolicy, QTextBrowser, QVBoxLayout, QWidget, QButtonGroup, QMessageBox, QFileDialog)
from websocket import create_connection
from modelscope import AutoModelForCausalLM, AutoTokenizer
from asr_widget import ASRWidget


class SummaryThread(QThread):
    summary_text_signal = Signal(bool, int, int, str)

    def __init__(self, text_file_path, model, tokenizer, summary_split_text, num_chunk_chars):
        super().__init__()
        self.text_file_path = text_file_path
        self.summary_split_text = summary_split_text
        self.model = model
        self.tokenizer = tokenizer

        self.num_chunk_chars = num_chunk_chars

    def run(self):
        device = 'cpu'

        with open(self.text_file_path, mode='r', encoding="utf8") as f:
            content = f.read()
        # record_text_list = content.split(self.summary_split_text)
        # num_split = len(record_text_list)
        # if num_split == 1 or num_split == 3:
        #     record_text = record_text_list[0]
        # else:
        #     record_text = record_text_list[-1]

        content = content.strip().replace(' ', '').replace('\u3000', '')
        if content == "":
            self.summary_text_signal.emit(False, 0, 0, " ")
        else:
            record_text_list = content.replace('！', '。').replace('？', '。').split('\n')
            history_len = 0
            record_text_list_input = ['']
            for text in record_text_list:
                num_char = len(text)
                # history_len += num_char
                if history_len + num_char > self.num_chunk_chars:
                    record_text_list_input.append(text)
                    history_len = num_char
                else:
                    record_text_list_input[-1] = record_text_list_input[-1] + text
                    history_len += num_char

            progress_total = len(record_text_list_input)
            self.summary_text_signal.emit(True, 0, progress_total, " ")
            summary_list = []
            for i, record_text in enumerate(record_text_list_input):
                if (i == len(record_text_list_input) - 1) and (len(record_text) < self.num_chunk_chars / 2):
                    record_text = content[-self.num_chunk_chars:]
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": record_text + "\n\n帮我生成这段会议记录文本的摘要"}
                ]
                text = self.tokenizer.apply_chat_template(
                    messages,
                    tokenize=False,
                    add_generation_prompt=True
                )
                model_inputs = self.tokenizer([text], return_tensors="pt").to(device)

                generated_ids = self.model.generate(
                    model_inputs.input_ids,
                    max_new_tokens=512
                )
                generated_ids = [
                    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
                ]
                summary = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
                summary_list.append(summary)
                if i < len(record_text_list_input) - 1:
                    self.summary_text_signal.emit(True, i + 1, progress_total, summary)
                else:
                    self.summary_text_signal.emit(False, i + 1, progress_total, summary)


class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app_name = "会议记录与摘要生成软件"
        self.version = "软著登记号：2023SR1804554 (v4.2)， 当前版本：5.0.1"
        self.home_dir = os.path.expanduser('~')
        # server related
        self.server_addr = 'your sherpa-1.2 server address'
        self.server_port = 8888

        # about summary model
        self.summary_split_text = "-" * 30 + " 摘要 " + "-" * 30
        self.history_summary = ""
        self.num_chunk_chars = 5000
        self.summary_thread = None
        self.summary_model_path = './Qwen1.5-0.5B-Chat'
        if not os.path.exists(self.summary_model_path):
            self.summary_model_path = os.path.join('./_internal', self.summary_model_path)
        self.summary_start_time = time.time()

        # summary_model
        self.summary_model = None
        self.tokenizer = None

        self.available_memory = psutil.virtual_memory().available / 1024 / 1024 / 1024
        if self.available_memory < 6:
            self.num_chunk_chars = 5000
        elif (self.available_memory >= 6) and (self.available_memory < 9):
            self.num_chunk_chars = 7500
        elif (self.available_memory >= 9) and (self.available_memory < 12):
            self.num_chunk_chars = 10000
        else:
            self.num_chunk_chars = 12000

        self.current_date = datetime.now().strftime("%Y-%m-%d")
        self.home_dir = os.path.expanduser('~')
        if not os.path.isdir(os.path.join(self.home_dir, 'Desktop')):
            os.makedirs(os.path.join(self.home_dir, 'Desktop'))
        self.init_asr_save_path = os.path.abspath(
            os.path.join(self.home_dir, f'Desktop/会议记录文本-{self.current_date}.txt'))

        self.resize(750, 620)
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
        self.path_text_input.setMinimumSize(QSize(0, 26))
        self.path_text_input.setMaximumSize(QSize(16777215, 26))
        self.path_text_input.setBaseSize(QSize(0, 0))
        self.path_text_input.setText(self.init_asr_save_path)
        self.text_save_path = self.init_asr_save_path

        self.main_widget_2_layout.addWidget(self.path_text_input)

        self.file_select_button = QPushButton(self.main_frame_2)
        self.file_select_button.setObjectName(u"file_select_button")
        self.file_select_button.setMinimumSize(QSize(64, 26))
        self.file_select_button.setMaximumSize(QSize(64, 26))
        self.file_select_button.setText(u"选择文件")
        self.file_select_button.clicked.connect(self.select_path)

        self.text_summary_button = QPushButton(self.main_frame_2)
        self.text_summary_button.setObjectName(u"text_summary_button")
        self.text_summary_button.setMinimumSize(QSize(84, 26))
        self.text_summary_button.setMaximumSize(QSize(84, 26))
        self.text_summary_button.setText(u"生成摘要")
        self.text_summary_button.clicked.connect(self.text_summary_start)

        self.main_widget_2_layout.addWidget(self.file_select_button)
        self.main_widget_2_layout.addWidget(self.text_summary_button)

        self.widget_file_select_right = QWidget(self.main_frame_2)
        self.widget_file_select_right.setObjectName(u"widget_file_select_right")

        self.main_widget_2_layout.addWidget(self.widget_file_select_right)

        self.main_widget_2_layout.setStretch(0, 2)
        self.main_widget_2_layout.setStretch(1, 9)
        self.main_widget_2_layout.setStretch(2, 1)
        self.main_widget_2_layout.setStretch(3, 0.2)
        self.main_widget_2_layout.setStretch(4, 1)
        self.main_widget_2_layout.setStretch(5, 2)

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

        # self.button_group = QButtonGroup(self)
        # self.show_related_group_box = QFrame(self.main_widget_3)
        # self.show_related_group_box.setObjectName(u"show_related_group_box")
        # self.show_related_group_box_layout = QHBoxLayout(self.show_related_group_box)
        # self.show_related_group_box_layout.setSpacing(0)
        # self.show_related_group_box_layout.setObjectName(u"show_related_group_box_layout")
        # self.show_related_group_box_layout.setContentsMargins(0, 0, 0, 0)
        # self.show_related_radio_frame1 = QFrame(self.show_related_group_box)
        # self.show_related_radio_frame1.setObjectName(u"show_related_radio_frame1")
        # self.show_related_radio_widget1_layout = QHBoxLayout(self.show_related_radio_frame1)
        # self.show_related_radio_widget1_layout.setSpacing(0)
        # self.show_related_radio_widget1_layout.setObjectName(u"show_related_radio_widget1_layout")
        # self.show_related_radio_widget1_layout.setContentsMargins(0, 0, 0, 0)
        # self.show_related_radio_button1 = QRadioButton(self.show_related_radio_frame1)
        # self.show_related_radio_button1.setObjectName(u"show_related_radio_button1")
        # sizePolicy1 = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # sizePolicy1.setHorizontalStretch(0)
        # sizePolicy1.setVerticalStretch(0)
        # sizePolicy1.setHeightForWidth(self.show_related_radio_button1.sizePolicy().hasHeightForWidth())
        # self.show_related_radio_button1.setSizePolicy(sizePolicy1)
        # self.show_related_radio_button1.setText(u"不显示字幕")
        # # if QT_CONFIG(shortcut)
        # self.show_related_radio_button1.setShortcut(u"")
        # # endif // QT_CONFIG(shortcut)
        # self.show_related_radio_button1.setChecked(True)

        # self.show_related_radio_widget1_layout.addWidget(self.show_related_radio_button1)

        # self.show_related_group_box_layout.addWidget(self.show_related_radio_frame1)
        #
        # self.show_related_radio_frame2 = QFrame(self.show_related_group_box)
        # self.show_related_radio_frame2.setObjectName(u"show_related_radio_frame2")
        # self.show_related_radio_widget2_layout = QHBoxLayout(self.show_related_radio_frame2)
        # self.show_related_radio_widget2_layout.setSpacing(0)
        # self.show_related_radio_widget2_layout.setObjectName(u"show_related_radio_widget2_layout")
        # self.show_related_radio_widget2_layout.setContentsMargins(0, 0, 0, 0)
        # self.show_related_radio_button2 = QRadioButton(self.show_related_radio_frame2)
        # self.show_related_radio_button2.setObjectName(u"show_related_radio_button2")
        # sizePolicy1.setHeightForWidth(self.show_related_radio_button2.sizePolicy().hasHeightForWidth())
        # self.show_related_radio_button2.setSizePolicy(sizePolicy1)
        # self.show_related_radio_button2.setText(u"显示字幕")
        # # if QT_CONFIG(shortcut)
        # self.show_related_radio_button2.setShortcut(u"")
        # # endif // QT_CONFIG(shortcut)
        #
        # self.show_related_radio_widget2_layout.addWidget(self.show_related_radio_button2)

        # self.show_related_group_box_layout.addWidget(self.show_related_radio_frame2)

        # self.show_related_radio_frame3 = QFrame(self.show_related_group_box)
        # self.show_related_radio_frame3.setObjectName(u"show_related_radio_frame3")
        # self.show_related_radio_widget3_layout = QHBoxLayout(self.show_related_radio_frame3)
        # self.show_related_radio_widget3_layout.setSpacing(0)
        # self.show_related_radio_widget3_layout.setObjectName(u"show_related_radio_widget3_layout")
        # self.show_related_radio_widget3_layout.setContentsMargins(0, 0, 0, 0)
        # self.show_related_radio_button3 = QRadioButton(self.show_related_radio_frame3)
        # self.show_related_radio_button3.setObjectName(u"show_related_radio_button3")
        # sizePolicy1.setHeightForWidth(self.show_related_radio_button3.sizePolicy().hasHeightForWidth())
        # self.show_related_radio_button3.setSizePolicy(sizePolicy1)
        # self.show_related_radio_button3.setText(u"显示展板")
        # # if QT_CONFIG(shortcut)
        # self.show_related_radio_button3.setShortcut(u"")
        # # endif // QT_CONFIG(shortcut)

        # self.show_related_radio_widget3_layout.addWidget(self.show_related_radio_button3)

        # self.button_group.addButton(self.show_related_radio_button1)
        # self.button_group.addButton(self.show_related_radio_button2)
        # self.button_group.addButton(self.show_related_radio_button3)

        # self.show_related_group_box_layout.addWidget(self.show_related_radio_frame3)
        #
        # self.main_widget_3_layout.addWidget(self.show_related_group_box)

        self.show_related_frame_left = QFrame(self.main_widget_3)
        self.show_related_frame_left.setObjectName(u"show_related_frame_left")

        self.main_widget_3_layout.addWidget(self.show_related_frame_left)

        self.main_widget_3_layout.setStretch(0, 1)
        self.main_widget_3_layout.setStretch(1, 2)
        self.main_widget_3_layout.setStretch(2, 1)

        # self.verticalLayout.addWidget(self.main_widget_3)

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
        self.main_widget_5_layout.setContentsMargins(5, 5, 5, 0)
        self.show_text_browser = QTextBrowser(self.main_widget_5)
        self.show_text_browser.setObjectName(u"show_text_browser")
        self.show_text_browser.setFrameShape(QFrame.NoFrame)
        self.show_text_browser.setMarkdown(u"")
        self.show_text_browser.setText(u"")
        self.show_text_browser.setTextInteractionFlags(Qt.TextSelectableByKeyboard | Qt.TextSelectableByMouse)
        self.show_text_browser.setPlaceholderText(u"")
        self.show_text_browser.setStyleSheet(u"background-color:rgba(255,255,255,0.618);color:rgb(0,0,0);")

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
        self.copyright_text_label.setText(self.version)
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
        # self.verticalLayout.setStretch(2, 3)
        self.verticalLayout.setStretch(2, 3)
        self.verticalLayout.setStretch(3, 15)
        self.verticalLayout.setStretch(4, 1)
        self.setCentralWidget(self.central_widget)

        # main thread
        self.asr_widget_started = False
        self.show_text = True
        self.asr_widget = None
        self.display_board = None
        self.asr_button.pressed.connect(self.asr_widget_control)

        QMetaObject.connectSlotsByName(self)

    def asr_widget_control(self):
        if not self.asr_widget_started:
            self.asr_button.setDisabled(True)
            self.text_summary_button.setDisabled(True)
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
            self.asr_widget.button_signal.connect(self.asr_widget_close)
            self.asr_widget.streaming_asr_thread.asr_record_text_signal.connect(self.set_asr_text_in_main_window)
            # # asr_widget show
            # if self.show_related_radio_button2.isChecked():
            #     self.asr_widget.show()
            # # display board, asr results depends on asr_widget
            # if self.show_related_radio_button3.isChecked():
            #     self.display_board = DisplayBoard()
            #     self.asr_widget.streaming_asr_thread.asr_record_text_signal.connect(self.display_board.set_display_text)
            #     self.display_board.close_signal.connect(self.display_board_close)
            #     self.display_board.show()

            self.asr_button.setText("关闭")
            self.asr_widget_started = True
            self.asr_button.setDisabled(False)
        else:
            self.text_summary_button.setDisabled(False)
            if self.asr_widget is not None:
                # asr results depends on asr_widget, so asr_widget is not None as long as ASR is started
                self.asr_widget.close()
            # if self.display_board is not None:
            #     self.display_board.close()
            #     self.display_board = None

    def asr_widget_close(self, closed: bool = False):
        if not closed:
            self.asr_button.setDisabled(True)
            self.asr_button.setText("正在关闭")
            self.asr_button.repaint()
            self.show_text_browser.setText("")
        else:
            self.asr_button.setText("启动")
            self.asr_widget_started = False
            self.asr_button.setDisabled(False)

    def display_board_close(self):
        if self.asr_widget is not None:
            # asr results depends on asr_widget, so asr_widget is not None as long as ASR is started
            self.asr_widget.close()
        self.display_board = None

    def select_path(self):
        file_path, file_type = QFileDialog.getOpenFileName(self, "选择识别文本存放的文件")
        if file_path != "":
            self.path_text_input.setText(os.path.abspath(file_path))

    def set_asr_text_in_main_window(self, asr_text_result):
        self.show_text_browser.setText(asr_text_result)
        self.show_text_browser.moveCursor(QtGui.QTextCursor.End)

    def closeEvent(self, event):
        if self.asr_widget is not None:
            self.asr_widget.close()
        if self.display_board is not None:
            self.display_board.close()

    def text_summary(self, start_tag, progress, progress_total, summary):
        # time related
        history_time = time.time() - self.summary_start_time
        self.summary_start_time = time.time()
        show_text_first = f"每{self.num_chunk_chars}字(本地)生成一个摘要，每个摘要需约3-15分钟，请耐心等待\n"
        show_text_first = show_text_first + "鼠标选中本页面（或将本页面置顶）可获得最快速度\n"
        left_time = round((progress_total - progress) * history_time / 60, 1)
        if (progress > 0) and (progress < progress_total):
            show_text_first = show_text_first + f"预估剩余{left_time}分钟\n"
        # update summary
        if progress == 0:
            self.history_summary = '\n\n' + self.summary_split_text + '\n'
            with open(self.text_save_path, mode='a', encoding="utf8") as f:
                f.write('\n\n' + self.summary_split_text + '\n')
        if start_tag:
            self.text_summary_button.setText(f"正在生成{progress}/{progress_total}")
            self.text_summary_button.setDisabled(True)
            self.asr_button.setDisabled(True)
            self.text_summary_button.repaint()
            self.asr_button.repaint()
            if progress > 0:
                self.history_summary = self.history_summary + '\n' + summary + '\n' + '-----' + '\n'
                with open(self.text_save_path, mode='a', encoding="utf8") as f:
                    f.write('\n' + summary + '\n' + '-----' + '\n')
        else:
            self.history_summary = self.history_summary + '\n' + summary + '\n\n' + self.summary_split_text + '\n'
            with open(self.text_save_path, mode='a', encoding="utf8") as f:
                f.write('\n' + summary + '\n')
                f.write('\n' + self.summary_split_text + '\n\n')
            self.text_summary_button.setText("生成摘要")
            self.text_summary_button.setDisabled(False)
            self.asr_button.setDisabled(False)
            self.text_summary_button.repaint()
            self.asr_button.repaint()
            if self.summary_thread is not None and not self.summary_thread.isFinished():
                self.summary_thread.exit()
        self.show_text_browser.setText(show_text_first + self.history_summary.strip())

    def text_summary_start(self):
        self.text_summary_button.setText("正在加载")
        self.text_summary_button.setDisabled(True)
        self.asr_button.setDisabled(True)
        self.text_summary_button.repaint()
        self.asr_button.repaint()
        self.text_save_path = self.path_text_input.text()
        if self.summary_model is None:
            try:
                # summary_model
                self.summary_model = AutoModelForCausalLM.from_pretrained(
                    self.summary_model_path,
                    device_map="auto"
                )
                self.tokenizer = AutoTokenizer.from_pretrained(self.summary_model_path)
            except:
                QMessageBox.critical(self, "错误", "摘要模型加载错误，可能是因为内存不足！")
                self.summary_model = None
                self.tokenizer = None
                # error, recovery state of text_summary_button
                self.text_summary_button.setText("生成摘要")
                self.text_summary_button.setDisabled(False)
                self.asr_button.setDisabled(False)
                self.text_summary_button.repaint()
                self.asr_button.repaint()

        if not os.path.isfile(self.text_save_path):
            QMessageBox.critical(self, "错误", f"文件{self.text_save_path}不存在！")
            # error, recovery state of text_summary_button
            self.text_summary_button.setText("生成摘要")
            self.text_summary_button.setDisabled(False)
            self.asr_button.setDisabled(False)
            self.text_summary_button.repaint()
            self.asr_button.repaint()
        else:
            self.summary_thread = SummaryThread(self.text_save_path, self.summary_model, self.tokenizer,
                                                self.summary_split_text, self.num_chunk_chars)
            self.summary_thread.summary_text_signal.connect(self.text_summary)
            self.summary_thread.start()


# 程序入口
if __name__ == "__main__":
    # 初始化QApplication，界面展示要包含在QApplication初始化之后，结束之前
    app = QApplication(sys.argv)
    app.setStyle(QtWidgets.QStyleFactory.create("Fusion"))
    icon_path = "icons/icon.png"
    if not os.path.exists(icon_path):
        icon_path = os.path.join('./_internal', icon_path)
    icon = QtGui.QIcon(icon_path)
    app.setWindowIcon(icon)

    # 初始化并展示我们的界面组件
    window = Ui_MainWindow()
    window.show()

    # 结束QApplication
    sys.exit(app.exec())
