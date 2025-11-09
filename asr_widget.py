# -*- coding: utf-8 -*-
import math
import sys
import time

import numpy
import pyaudio
from PySide6.QtCore import (QRect, Qt, QThread, Signal)
from PySide6.QtGui import (QPainter, QMouseEvent)
from PySide6.QtWidgets import (QApplication, QLabel, QWidget, QStyleOption, QStyle)

from main_thread import MicrophoneRecordThread, WebSocketSendThread, WebSocketRecvThread
from paddle_punctuation.predictor import PunctuationExecutor


class StreamingASRThread(QThread):
    asr_caption_text_signal = Signal(str)
    asr_record_text_signal = Signal(str)

    def __init__(self, server_addr: str, server_port: int, seconds_per_chunk: float = 0.1, device_id: int = -1,
                 resample_rate: int = 16000, format: int = pyaudio.paInt16,
                 show_lines: int = 3, line_length: int = 35, text_save_path: str = './asr_result.txt'):
        super(StreamingASRThread, self).__init__()
        self.thread_started = False
        self.server_addr = server_addr
        self.server_port = server_port
        self.seconds_per_chunk = seconds_per_chunk
        self.resample_rate = resample_rate
        self.format = format
        self.is_wss = True
        self.text_save_path = text_save_path

        self.p = pyaudio.PyAudio()
        if device_id > 0:
            self.record_device_info = self.p.get_device_info_by_index(device_id)
        else:
            self.record_device_info = self.p.get_default_input_device_info()
        self.device_id = int(self.record_device_info['index'])
        self.channels = int(self.record_device_info['maxInputChannels'])
        self.record_rate = int(self.record_device_info['defaultSampleRate'])
        # whether support resample_rate
        self.support_resample_rate = False
        try:
            self.support_resample_rate = self.p.is_format_supported(rate=self.resample_rate,
                                                                    input_device=self.device_id,
                                                                    input_channels=self.channels,
                                                                    input_format=self.format)
        except:
            self.support_resample_rate = False
        # if support resample_rate, record with resample_rate
        if self.support_resample_rate:
            self.record_rate = self.resample_rate
        # thread init
        self.record_thread = MicrophoneRecordThread(seconds_per_chunk=self.seconds_per_chunk, channels=self.channels,
                                                    record_rate=self.record_rate,
                                                    format=self.format, device_id=self.device_id)
        self.send_thread = WebSocketSendThread(record_thread=self.record_thread, server_addr=self.server_addr,
                                               server_port=self.server_port, resample_rate=self.resample_rate,
                                               is_wss=self.is_wss)
        self.recv_thread = WebSocketRecvThread(self.send_thread)
        self.punctuations = {'，', '。', '？', '！', '、'}
        self.asr_current_result = dict()
        self.asr_current_text = ''
        self.asr_current_text_punc = ''
        # text to text_with_punc
        self.asr_current_text_idx = []
        # text_with_punc to text
        self.asr_current_text_punc_idx = []

        self.history_result_list = []
        self.history_text = ''
        self.history_text_list = []
        # text to text_with_punc
        self.history_text_idx = []
        self.history_text_idx_list = []
        self.history_text_punc = ''
        self.history_text_punc_list = []
        # text_with_punc to text
        self.history_text_punc_idx = []
        self.history_text_punc_idx_list = []
        self.history_text_punc_split = ''
        self.space = u'\u3000'
        self.spaces_num = 2
        self.history_text_length = 0
        self.history_text_punc_length = 0

        self.thread_open_signal = True

        # start index in self.history_text_punc for text showing
        self.show_start_idx = 0
        self.show_lines = show_lines
        self.line_length = line_length
        self.max_show_length = self.show_lines * self.line_length

        model_dir = './pun_models'
        tokenizer_dir = './ernie-3.0-medium-zh'
        self.pun_executor = PunctuationExecutor(model_dir=model_dir, tokenizer_dir=tokenizer_dir, use_gpu=False)
        self.thread_started = True
        self.text_show = ''
        self.text_show_lines = []

    def run(self):
        self.record_thread.start()
        self.send_thread.start()
        self.recv_thread.start()
        while self.thread_open_signal:
            if self.recv_thread.isRunning():
                recv_result = self.recv_thread.result
                recv_text = self.recv_thread.result_text
                # save history (if needed) and update if asr_current_text changed
                if recv_text != self.asr_current_text:
                    # when segment > current segment and current_text not empty, append current result to history
                    if self.asr_current_result.get('segment') is not None and recv_result.get(
                            'segment') is not None and (
                            (recv_result['segment'] > self.asr_current_result['segment']) and (
                            self.asr_current_text != '')):
                        # write asr text to file when segment
                        with open(self.text_save_path, encoding='utf-8', mode='a') as f:
                            f.write(self.space * self.spaces_num + self.asr_current_text_punc + '\n')
                        self.history_result_list.append(self.asr_current_result)
                        self.history_text = self.history_text + self.asr_current_text
                        self.history_text_list.append(self.asr_current_text)
                        self.history_text_idx.extend(self.asr_current_text_idx)
                        self.history_text_idx_list.append(self.asr_current_text_idx)
                        self.history_text_punc = self.history_text_punc + self.asr_current_text_punc
                        self.history_text_punc_list.append(self.asr_current_text_punc)
                        self.history_text_punc_idx.extend(self.asr_current_text_punc_idx)
                        self.history_text_punc_idx_list.append(self.asr_current_text_punc_idx)
                        self.history_text_punc_split = (self.history_text_punc_split + self.space * self.spaces_num +
                                                        self.asr_current_text_punc + '\n')
                        self.history_text_length = len(self.history_text)
                        self.history_text_punc_length = len(self.history_text_punc)

                    # update current result and so on
                    self.asr_current_result = recv_result.copy()
                    if recv_text != '':
                        self.asr_current_text_punc = self.pun_executor(recv_text)
                    else:
                        self.asr_current_text_punc = ''
                    # update asr_current_text
                    self.asr_current_text = recv_text
                    # compute asr_current_text_idx which means idx of each char in asr_current_text_punc
                    self.asr_current_text_idx = []
                    self.asr_current_text_punc_idx = []
                    if self.asr_current_text != '':
                        punc_idx = self.history_text_length
                        for i in range(len(self.asr_current_text_punc)):
                            # if current_text_punc[i] is not punctuation
                            if self.asr_current_text_punc[i] not in self.punctuations:
                                # text to text_with_punc
                                self.asr_current_text_idx.append(i + self.history_text_punc_length)
                                # text_with_punc to text
                                self.asr_current_text_punc_idx.append(punc_idx)
                                punc_idx += 1
                            else:
                                self.asr_current_text_punc_idx.append(-1)

                    # emit text show
                    text_all = self.history_text + self.asr_current_text
                    text_all_idx = self.history_text_idx + self.asr_current_text_idx
                    punc_text_all = self.history_text_punc + self.asr_current_text_punc
                    punc_text_all_idx = self.history_text_punc_idx + self.asr_current_text_punc_idx
                    len_punc_text_all = len(punc_text_all_idx)
                    if self.show_start_idx >= len(text_all_idx):
                        self.text_show = ''
                        text_show_line_split = ''
                    else:
                        punc_text_start_idx = text_all_idx[self.show_start_idx]
                        show_length = len_punc_text_all - punc_text_start_idx
                        if show_length > self.max_show_length:
                            overflow_length = show_length - self.max_show_length
                            overflow_lines = math.ceil(float(overflow_length) / self.line_length)
                            punc_text_start_idx += overflow_lines * self.line_length
                            while punc_text_all[punc_text_start_idx] in self.punctuations:
                                punc_text_start_idx += 1
                            # get new text idx of new start char in punc text
                            self.show_start_idx = punc_text_all_idx[punc_text_start_idx]
                        self.text_show = punc_text_all[punc_text_start_idx:]
                        len_text_show = len(self.text_show)
                        # split text show to lines
                        self.text_show_lines = []
                        line_start_idx = [0]
                        idx = 0
                        while idx <= len_text_show - 1:
                            idx += self.line_length
                            if idx <= len_text_show - 1:
                                if self.text_show[idx] in self.punctuations:
                                    idx += 1
                            line_start_idx.append(idx)
                        for i in range(len(line_start_idx) - 1):
                            self.text_show_lines.append(self.text_show[line_start_idx[i]:line_start_idx[i + 1]])
                        text_show_line_split = '\n'.join(self.text_show_lines)
                    self.asr_caption_text_signal.emit(text_show_line_split[0:-1])
                    if self.asr_current_text_punc == '':
                        self.asr_record_text_signal.emit(self.history_text_punc_split)
                    else:
                        self.asr_record_text_signal.emit(
                            self.history_text_punc_split + self.space * self.spaces_num +
                            self.asr_current_text_punc[0:-1] + '\n')
            time.sleep(0.01)

        # update history result before stopping thread
        self.history_result_list.append(self.asr_current_result)
        self.history_text_punc = self.history_text_punc + self.asr_current_text_punc

        # write asr text to file and update history before stopping thread
        if self.asr_current_text != '':
            with open(self.text_save_path, encoding='utf-8', mode='a') as f:
                f.write(self.space * self.spaces_num + self.asr_current_text_punc + '\n')
            self.history_result_list.append(self.asr_current_result)
            self.history_text = self.history_text + self.asr_current_text
            self.history_text_list.append(self.asr_current_text)
            self.history_text_idx.extend(self.asr_current_text_idx)
            self.history_text_idx_list.append(self.asr_current_text_idx)
            self.history_text_punc = self.history_text_punc + self.asr_current_text_punc
            self.history_text_punc_list.append(self.asr_current_text_punc)
            self.history_text_punc_idx.extend(self.asr_current_text_punc_idx)
            self.history_text_punc_idx_list.append(self.asr_current_text_punc_idx)
            self.history_text_punc_split = (self.history_text_punc_split + self.space * self.spaces_num +
                                            self.asr_current_text_punc + '\n')
            self.history_text_length = len(self.history_text)
            self.history_text_punc_length = len(self.history_text_punc)
        # stop thread
        self.recv_thread.recv_signal = False
        self.send_thread.ws_open_signal = False
        self.record_thread.record_signal = False

        self.recv_thread.wait()
        self.record_thread.wait()
        self.send_thread.wait()


# 继承QWidget类，以获取其属性和方法
class ASRWidget(QWidget):
    button_signal = Signal(bool)

    def __init__(self, server_addr: str = '127.0.0.1', server_port: int = 18001,
                 text_save_path: str = './asr_result.txt', device_id: int = -1):
        super().__init__()
        # asr server info
        self.server_addr = server_addr
        self.server_port = server_port
        self.seconds_per_chunk = 0.1
        self.device_id = device_id

        # show related
        self.window_width = 1480
        self.window_height = 180
        self.show_lines = 3
        self.line_length = 35
        self.text_save_path = text_save_path

        # drag related
        self.drag = False
        self.window_pos = None
        self.mouse_start_pt = None
        # channels select
        # self.channels_weight = numpy.array([2.0, 2.0, 2.0, 2.0]).astype(numpy.float32)
        # window settings
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowOpacity(0.9)
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # window
        self.setWindowTitle("字幕")
        self.resize(self.window_width, self.window_height)
        # label
        self.asr_text_label = QLabel(parent=self)
        self.asr_text_label.setObjectName(u"label")
        self.asr_text_label.setGeometry(QRect(0, 0, self.window_width, self.window_height))
        self.asr_text_label.setWordWrap(True)
        self.asr_text_label.setMouseTracking(True)
        self.asr_text_label.setDisabled(True)
        self.asr_text_label.setScaledContents(True)
        self.asr_text_label.setContentsMargins(20, 12, 0, 0)
        self.asr_text_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.asr_text_label.setStyleSheet("font-size:30pt; color:rgba(255,255,255,0.618);")

        self.streaming_asr_thread = StreamingASRThread(self.server_addr, self.server_port, self.seconds_per_chunk,
                                                       device_id=self.device_id, show_lines=self.show_lines,
                                                       line_length=self.line_length, text_save_path=self.text_save_path)
        self.streaming_asr_thread.setParent(self)
        self.streaming_asr_thread.start()
        self.streaming_asr_thread.send_thread.channels_weight = (
                self.streaming_asr_thread.send_thread.channels_weight * 2).astype(numpy.float32)
        self.streaming_asr_thread.asr_caption_text_signal.connect(self.asr_text_label.setText)

        self.setStyleSheet("ASRWidget{background:rgba(0,0,0,0.382); border-radius:10px;}")

    def stop_asr(self):
        self.streaming_asr_thread.thread_open_signal = False
        self.streaming_asr_thread.wait()

    def closeEvent(self, event):
        self.streaming_asr_thread.thread_open_signal = False
        self.button_signal.emit(False)
        self.streaming_asr_thread.wait()
        self.button_signal.emit(True)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.mouse_start_pt = event.globalPosition().toPoint()
            self.window_pos = self.frameGeometry().topLeft()
            self.drag = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag:
            distance = event.globalPosition().toPoint() - self.mouse_start_pt
            self.move(self.window_pos + distance)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag = False

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)
        super().paintEvent(event)


# 程序入口
if __name__ == "__main__":
    # 初始化QApplication，界面展示要包含在QApplication初始化之后，结束之前
    app = QApplication(sys.argv)

    # 初始化并展示我们的界面组件
    window = ASRWidget()
    window.show()

    # 结束QApplication
    sys.exit(app.exec())
