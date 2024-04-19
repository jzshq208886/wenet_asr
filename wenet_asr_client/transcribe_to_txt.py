import os
import wave
import time
from datetime import datetime

from lib import wenet_asr_client

IP_PORT = "192.168.81.10:50051"

def cal_chunk(time_interval, framerate, sampwidth):
    # # 计算每个时间间隔内需要读取的样本数
    # samples_per_interval = time_interval * framerate

    # # 计算每个时间间隔内需要读取的字节数
    # bytes_per_interval = samples_per_interval * sampwidth

    # 返回每个时间间隔内需要读取的字节数
    return time_interval * framerate


def read_long_audio(audio_dir, sep_dur=10):
    datastream = []

    with wave.open(audio_dir, 'rb') as f:
        samprate = f.getframerate()
        sampwidth = f.getsampwidth()
        chunk = cal_chunk(sep_dur, samprate, sampwidth)
        chunk = 81920
        print(f'chunk: {chunk}')

        while True:
            dataframes = f.readframes(chunk)
            if not dataframes:
                break
            if len(dataframes) < chunk / 3:
                datastream[-1] += dataframes
            else:
                datastream.append(dataframes)
    
    return datastream, samprate, sampwidth


def transcribe_to_txt(recognizer, audio_dir, filename):
    datastream, samprate, sampwidth = read_long_audio(audio_dir)
    print(len(datastream))
    
    recognizer.sample_rate = samprate
    recognizer.bit_depth = sampwidth * 8
    
    print('recognizing...')
    text = ''
    for data in datastream:
        print('len', len(data))
        result = recognizer.recognize(data)
        print(result)
        text += result
    print(f'result: {text}')

    try:
        with open(filename, 'w') as file:
            file.write(text)
        print(f"文件 '{filename}' 已成功创建并写入内容。")
    except Exception as e:
        print(f"写入文件 '{filename}' 时出错：{e}")


if __name__ == '__main__':
    recognizer = wenet_asr_client.Recognizer(
        sample_rate=None,
        bit_depth=None,
    )

    print('connecting...')
    recognizer.connect(IP_PORT)
    recognizer.reload_model(
        hotwords='default',
        context_score=6,
    )

    # audio_dir = 'audio/samples3/1702257074_2632_70_0_1.wav'
    # transcribe_to_txt(recognizer, audio_dir, 'transcript/1702257074_2632_70_0_1.txt')

    samples = 'samples2'
    audio_path = f'audio/{samples}'
    txt_path = f'transcript_3/{samples}'
    # txt_path = 'transcript/samples3'
    if not os.path.exists(txt_path):
        os.makedirs(txt_path)
    for filename in os.listdir(audio_path):
        if not filename.endswith('.wav'):
            continue
        print(f'\ncurrent: {filename}')
        audio_dir = os.path.join(audio_path, filename)
        transcribe_to_txt(recognizer, audio_dir, os.path.join(txt_path, filename.strip('.wav') + '.txt'))
