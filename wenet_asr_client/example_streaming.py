import wave
import time
from datetime import datetime

from lib import wenet_asr_client


SERVER_IP = '192.168.81.10'  # 服务器IP地址
SERVER_PORT = 50051       # 服务器端口号

# 设置音频参数
# CHANNELS = 1               # 声道数为1（单声道）
# RATE = 8000                # 采样率为8k

# 每次读取的音频帧大小
# 用于控制识别结果实时更新速率，CHUNK越小实时更新率越高，但应保证实时更新时间间隔大于一次性识别请求的时长
CHUNK = 1024 * 16

AUDIO_FILE = 'audio/082311171430575628101.wav'

def streaming_test():

    # 按指定CHUNK大小切割读取.wav文件，模拟实时数据流
    print('reading audio...')
    datastream = []
    with wave.open(AUDIO_FILE, 'rb') as f:
        rate = f.getframerate()  # 使用.wav文件模拟数据流时，数据采样率为.wav文件的采样率;实际应用时应使用实际数据流的采样率（8k）
        channels = f.getnchannels()
        sampwidth = f.getsampwidth()
        duration = 0

        first = True
        while True:
            dataframes = f.readframes(CHUNK)
            if not dataframes:
                break

            if first:
                first = False
                num_frames = len(dataframes) / channels / sampwidth
                duration = num_frames / rate  # 每个CHUNK对应的音频时长(s)
            
            datastream.append(dataframes)
    print(f'Sample rate: {rate}')
    print(f'Channels: {channels}')
    print(f'Sample width: {sampwidth}')
    print(f'CHUNK duration: {duration}(s)')


    # 初始化一个Recognizer对象，需指定待识别音频的采样率和位深度。仅支持单声道，多声道音频需提前转换为单声道。
    recognizer = wenet_asr_client.Recognizer(sample_rate=rate,
                                             bit_depth=8 * sampwidth,
                                             update_duration=8)

    # 连接服务器
    print('connecting...')
    recognizer.connect(f'{SERVER_IP}:{SERVER_PORT}')

    # recognizer.reload_model(context_score=6)

    # 开启流式识别模式
    recognizer.start_streaming()

    # 流式识别模式下，按CHUNK持续输入数据流至Recognizer对象，每次输入后自动执行伪流式识别逻辑
    print('recognizing...')
    ini_time = datetime.now()
    time.sleep(duration)  # 模拟等待第一个CHUNK的时长
    for data in datastream:
        chunkStart = time.time()

        recognizer.input(data)  # 输入一个CHUNK的数据，并自动执行伪流式识别逻辑
        result = recognizer.result
        fixed, puncted, new = result['fixed'], result['puncted'], result['new']
        print(f'[{datetime.now()-ini_time}] [{fixed}]{puncted}')  # 打印时间和结果
        # print(f'[{datetime.now()-ini_time}] [{fixed}]{new}')  # 打印时间和结果

        # 补全一个CHUNK音频的实际时长
        run_delay = time.time() - chunkStart
        print('run_delay:', run_delay)
        if run_delay > duration:
            print('Warning: Single recognition request duration is longer than CHUNK duration. Try to set the CHUNK larger.')
        else:
            time.sleep(duration - run_delay)

    # 断开链接
    recognizer.disconnect()


if __name__ == '__main__':
    streaming_test()
