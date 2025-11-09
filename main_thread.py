# -*- coding: utf-8 -*-
import json
import ssl
import time

import numpy
import pyaudio
from queue import Queue
from websocket import ABNF, create_connection
import samplerate
from PySide6.QtCore import QThread


class MicrophoneRecordThread(QThread):
    """ xxx

        Author: Wang Zifan
        Date: 2023/09/08

        Attributes:
            xxx
    """

    def __init__(self, seconds_per_chunk: float = 0.1, channels: int = 1, record_rate: int = 48000,
                 format: int = pyaudio.paInt16, device_id: int = 0):
        super(MicrophoneRecordThread, self).__init__()
        # record info
        self.seconds_per_chunk = seconds_per_chunk
        self.channels = channels
        self.record_rate = record_rate
        self.format = format
        self.device_id = device_id
        self.p = pyaudio.PyAudio()
        self.chunk = int(record_rate * seconds_per_chunk)
        self.record_queue = Queue()
        self.record_signal = True

    def run(self):
        # 打开录音流
        stream = self.p.open(format=self.format,
                             channels=self.channels,
                             rate=self.record_rate,
                             input=True,
                             input_device_index=self.device_id,
                             frames_per_buffer=self.chunk)
        while self.record_signal:
            # record
            data = stream.read(self.chunk)
            self.record_queue.put(data)


class WebSocketSendThread(QThread):
    """ xxx

        Author: Wang Zifan
        Date: 2023/09/08

        Attributes:
            xxx
    """

    def __init__(self, record_thread: MicrophoneRecordThread, server_addr: str, server_port: int,
                 resample_rate: int = 16000, is_wss: bool = False):
        super(WebSocketSendThread, self).__init__()
        self.record_thread = record_thread
        # init server
        self.server_addr = server_addr
        self.server_port = server_port
        self.is_wss = is_wss
        if is_wss:
            self.ws_url = f"wss://{server_addr}:{server_port}"
            self.ws = create_connection(self.ws_url, sslopt={"cert_reqs": ssl.CERT_NONE})
        else:
            self.ws_url = f"ws://{server_addr}:{server_port}"
            self.ws = create_connection(self.ws_url)
        self.ws_open_signal = True
        self.resample_rate = resample_rate
        channels = self.record_thread.channels
        self.channels_weight = (numpy.array([1.0] * channels) / channels).astype(numpy.float32)

    def run(self):
        while True:
            # if signal is open
            if self.ws_open_signal:
                # if websocket is closed, connect websocket server
                if not self.ws.connected:
                    if self.is_wss:
                        self.ws = create_connection(self.ws_url, sslopt={"cert_reqs": ssl.CERT_NONE})
                    else:
                        self.ws = create_connection(self.ws_url)
                # if websocket is connected, get data from record_queue and send it to server
                else:
                    # if record queue is not empty (only at this state, WebSocketRecvThread can receive message)
                    if not self.record_thread.record_queue.empty():
                        # get chunk data
                        chunk_data = self.record_thread.record_queue.get()
                        # send data to websocket server
                        self.send_chunk_data(chunk_data)
            # if signal is close
            else:
                # self.ws.send("Done")
                self.ws.close()
                break
            time.sleep(0.001)

    def send_chunk_data(self, chunk_data):
        # convert chunk data to numpy format
        if self.record_thread.format == pyaudio.paInt16:
            data = numpy.frombuffer(chunk_data, dtype=numpy.int16).astype(numpy.float32) / (2 ** 15)
        elif self.record_thread.format == pyaudio.paInt32:
            data = numpy.frombuffer(chunk_data, dtype=numpy.int32).astype(numpy.float32) / (2 ** 31)
        elif self.record_thread.format == pyaudio.paFloat32:
            data = numpy.frombuffer(chunk_data, dtype=numpy.float32)
        else:
            # default
            data = numpy.frombuffer(chunk_data, dtype=numpy.int16).astype(numpy.float32) / (2 ** 15)

        # reshape for channels (num_frames, channels)
        data = data.reshape(-1, self.record_thread.channels)
        # apply weighted summation to channels
        data = numpy.matmul(data, self.channels_weight.reshape(-1, 1)).flatten()
        # if record rate is not resample rate (usually 16000), resample data to resample rate
        if self.record_thread.record_rate != self.resample_rate:
            data = samplerate.resample(data, self.resample_rate / self.record_thread.record_rate)
        # send data to websocket server
        self.ws.send(data.astype(numpy.float32).tobytes(), opcode=ABNF.OPCODE_BINARY)


class WebSocketRecvThread(QThread):
    """ xxx

        Author: Wang Zifan
        Date: 2023/09/08

        Attributes:
            xxx
    """

    def __init__(self, send_thread: WebSocketSendThread):
        super(WebSocketRecvThread, self).__init__()
        self.send_thread = send_thread
        self.result = dict()
        self.result_text = ''
        self.recv_signal = True

    def run(self):
        while self.recv_signal:
            # if open_signal of send_thread is True and websocket of send_thread is connected
            if self.send_thread.ws.connected:
                # get message
                try:
                    message = self.send_thread.ws.recv()
                except:
                    continue
                # if message is not empty string, json parsing
                if message != '':
                    message_json = json.loads(message)
                    self.result = message_json
                    self.result_text = message_json['text']
                # if message is empty string, result is empty
                else:
                    self.result = dict()
                    self.result_text = ''
            time.sleep(0.001)


class StreamingASRThread(QThread):
    # asr_text_signal = Signal(str)

    def __init__(self, server_addr: str, server_port: int, seconds_per_chunk: float = 0.1, device_id: int = -1,
                 resample_rate: int = 16000, format: int = pyaudio.paInt16):
        super(StreamingASRThread, self).__init__()
        self.server_addr = server_addr
        self.server_port = server_port
        self.seconds_per_chunk = seconds_per_chunk
        self.resample_rate = resample_rate
        self.format = format

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
                                               server_port=self.server_port, resample_rate=self.resample_rate)
        self.recv_thread = WebSocketRecvThread(self.send_thread)
        self.asr_text = ''
        self.thread_open_signal = True

    def run(self):
        self.record_thread.start()
        self.send_thread.start()
        self.recv_thread.start()
        while self.thread_open_signal:
            if self.recv_thread.isRunning():
                self.asr_text = self.recv_thread.result_text
                # self.asr_text_signal.emit(self.asr_text)
            time.sleep(0.005)
        self.record_thread.record_signal = False
        self.send_thread.ws_open_signal = False
        self.recv_thread.recv_signal = False
        self.record_thread.wait()
        self.send_thread.wait()
        self.recv_thread.wait()


if __name__ == "__main__":
    server_addr = '127.0.0.1'
    server_port = 8888
    seconds_per_chunk = 0.2

    streaming_asr_thread = StreamingASRThread(server_addr=server_addr, server_port=server_port,
                                              seconds_per_chunk=seconds_per_chunk)
    streaming_asr_thread.send_thread.channels_weight = numpy.array([0, 0, 0.5, 0.5]).astype(numpy.float32)
    streaming_asr_thread.start()
    streaming_asr_thread.wait()
