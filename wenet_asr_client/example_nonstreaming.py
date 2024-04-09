import wave

from lib.wenet_asr_client import Recognizer

IP_PORT = "192.168.81.10:50051"
# IP_PORT = "localhost:50051"
AUDIO_FILE = 'audio/zh.wav'

def nonstreaming_test():
    # 将待识别语音读取为bytes类型
    with wave.open(AUDIO_FILE, 'rb') as f:
        rate = f.getframerate()
        data = f.readframes(f.getnframes())

    # 初始化一个Recognizer对象
    recognizer = Recognizer(sample_rate=rate)

    # 连接服务器
    print('connecting...')
    recognizer.connect(IP_PORT)

    # 请求执行单次语音识别
    print('recognizing...')
    result = recognizer.recognize(data, punctuation=True)

    # 打印单次识别结果
    print(f'result:{result}')
    recognizer.disconnect()

if __name__ == '__main__':
    nonstreaming_test()
