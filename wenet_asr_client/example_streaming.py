import wave
import time
from datetime import datetime

from recognizer import Recognizer


SERVER_IP = 'localhost'  # 服务器IP地址
SERVER_PORT = 50051       # 服务器端口号

"""
CHUNK: 模拟实时音频流时，每次读取的音频帧大小
用于控制一次接收的音频流长度，影响接收音频流间隔，从而控制识别结果实时更新速率
CHUNK越小实时更新率越高，但应保证实时更新时间间隔大于一次性识别请求的时长
"""
CHUNK = 1024 * 16

AUDIO_FILE = 'audio/082311171430575628101.wav'


def audio_stream_simulate(file_path, chunk):
    '''
    This function is used for simulating real-time audio stream from an audio file.
    '''
    # 按指定CHUNK大小切割读取.wav文件，模拟实时数据流
    print('reading audio...')
    datastream = []
    with wave.open(file_path, 'rb') as f:
        samprate = f.getframerate()  # 使用.wav文件模拟数据流时，数据采样率为.wav文件的采样率;实际应用时应使用实际数据流的采样率（8k）
        channels = f.getnchannels()
        sampwidth = f.getsampwidth()
        duration = 0

        first = True
        while True:
            dataframes = f.readframes(chunk)
            if not dataframes:
                break

            if first:
                first = False
                num_frames = len(dataframes) / channels / sampwidth
                duration = num_frames / samprate  # 每个CHUNK对应的音频时长(s)
            
            datastream.append(dataframes)
    print(f'Sample rate: {samprate}')
    print(f'Channels: {channels}')
    print(f'Sample width: {sampwidth}')
    print(f'CHUNK duration: {duration}(s)')
    return datastream, samprate, sampwidth, duration


def streaming_test():
    # 使用音频文件模拟实时音频流
    datastream, samprate, sampwidth, duration = audio_stream_simulate(AUDIO_FILE, CHUNK)

    # 初始化一个Recognizer对象，需指定待识别音频的采样率和位深度。仅支持单声道，多声道音频需提前转换为单声道。
    recognizer = Recognizer(sample_rate=samprate,
                            bit_depth=8 * sampwidth,
                            update_duration=8)

    # 连接服务器
    print('connecting...')
    recognizer.connect(f'{SERVER_IP}:{SERVER_PORT}')

    # recognizer.reload_model(context_score=6)

    # 开启流式识别模式
    recognizer.start_streaming()

    # 流式识别模式下，按CHUNK持续输入数据流至Recognizer对象，每次输入后自动执行流式识别逻辑
    print('recognizing...')
    ini_time = datetime.now()  # 记录开始时间
    time.sleep(duration)  # 模拟实时数据流，等待第一个CHUNK的时长

    for data in datastream:
        chunkStart = time.time()  # 记录该CHUNK输入时的时间

        # 输入新音频数据，自动执行实时识别逻辑
        recognizer.input(data)  # 输入一个CHUNK的数据，并自动执行流式识别逻辑，包括音频合并、转写、截断固定、标点预测等
        
        # 获取当前结果
        result = recognizer.result  # 获取当前已获取部分音频流的总转写结果
        fixed, puncted, new = result['fixed'], result['puncted'], result['new']
        print(f"[{datetime.now()-ini_time}] [{fixed}]{puncted}{new}")  # 打印时间和结果（格式：[总时间] [标点固定部分]标点可变部分+文本可变部分）
        # print(f"[{datetime.now()-ini_time}] [{fixed}]{new}")  # （无标点情况下）打印时间和结果（格式：[总时间] [文本固定部分]文本可变部分）

        # 模拟实时数据流，延迟一个CHUNK音频的实际时长
        run_delay = time.time() - chunkStart
        print('run_delay:', run_delay)
        if run_delay > duration:
            print(f'[WARNING]: Single recognition request duration ({run_delay}) is longer than CHUNK duration ({duration}). (RTF>1.) Try to set CHUNK larger to avoid this.')
        else:
            time.sleep(duration - run_delay)

    # 断开链接
    recognizer.disconnect()


if __name__ == '__main__':
    streaming_test()
