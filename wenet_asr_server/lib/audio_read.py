import pyaudio
import wave
import time
import numpy as np
import torch
# from typing import Union

# CHUNK = 1024  # 每次读取的音频数据块大小
# FORMAT = pyaudio.paInt16  # 音频格式
# CHANNELS = 1  # 声道数

def read_by_bytes(audio_file: str, length: int = None) -> tuple[torch.Tensor, int]:
    wav_file = wave.open(audio_file, 'rb')
    frame_rate = wav_file.getframerate()

    with open(audio_file, 'rb') as f:
        if length is None:
            data = f.read()
        else:
            data = f.read(length)

    return bytes2tensor(data), frame_rate

def to_stream(audio_name: str, chunk=1024) -> tuple[pyaudio.Stream, int]:
    wf = wave.open(audio_name, 'rb')
    rate = wf.getframerate()
    
    # 初始化音频流
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=rate,
                    output=True,
                    input=True)
    
    # # 实时发送音频数据流
    data = wf.readframes(chunk)
    while data:
        stream.write(data)  # 播放音频
        data = wf.readframes(chunk)
        # time.sleep(len(data) / float(rate))
    return stream, rate


def bytes2tensor(data: bytes) -> torch.Tensor:
    waveform = np.frombuffer(data, dtype=np.int16)
    waveform = waveform.astype(np.float32)  # 转换数据类型为32位浮点数
    waveform = torch.from_numpy(waveform)  # 转换为torch Tensor
    return waveform.unsqueeze(0)  # 添加batch维度，假设没有通道维度


def send_audio_stream():
    # 连接服务端
    server_address = ('localhost', 12345)  # 服务端地址和端口
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(server_address)

    # 打开音频文件
    wf = wave.open(WAVE_FILENAME, 'rb')

    # 初始化音频流
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # 实时发送音频数据流
    data = wf.readframes(CHUNK)
    while data:
        client_socket.sendall(data)  # 发送音频数据
        stream.write(data)  # 播放音频
        data = wf.readframes(CHUNK)
        time.sleep(len(data) / float(RATE))  # 按音频播放速率延迟发送数据

    # 关闭连接
    client_socket.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf.close()

if __name__ == "__main__":
    # send_audio_stream()
    pass