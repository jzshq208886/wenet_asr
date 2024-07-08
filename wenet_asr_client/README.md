 # WeNet ASR Client

The client project provides python API implemented by a python class. Encapsulating systematic usage of the API service provided by **WeNet ASR Server**, the API not only supports single-time model call, but also provides a real-time ASR calling method.

## Environment Installation

Run the following command to install python packages in a newly created conda environment:

```bash
pip install -r requirements.txt  # Note: run this command in wenet_asr_client directory.
```

## API Usage

> Before you start using *WeNet ASR Client*, you need to run the service provided by *WeNet ASR Server* on a server. （Please refer to *wenet_asr_server/README.md*.） After that, you can follow the instruction below to use ASR service through client API.

Import the **Recognizer** class from *recognizer.py*, and instantiate a *recognizer* instance.

```python
from recognizer import Recognizer
recognizer = Recognizer(sample_rate=samprate, bit_depth=8 * sampwidth)
```

Class **Recognizer** has 4 initialization arguments.
> **sample_rate**: *int*, the sample rate of the audio you need to transfer.<br>
> **bit_depth**: *int*, the bit depth (8 times sample width) of the audio you need to transfer.<br>
> **update_duration**: *int*, time intervals of text truncation and fix. Only takes effect in real-time call.<br>
> **puncting_len**: *int*, truncation length to fix the punctuation prediction. Only takes effect in real-time call.

The properties can also be configured or modified later. Only mono audio is supported. If you need to transcribe multichannel audio, convert to mono before input.

Next, connect to the server.
```python
recognizer.connect(IP_PORT)
```
The format of the argument IP_PORT is "{ip}:{port}". Example: "192.168.81.10:50051"

### Single-time Call

```python
recognizer.recognize(audio, punctuation=True)
```

*Recognizer.recognize()* method accepts two arguments.
> **audio**: *bytes*. The audio data of type *bytes*.<br>
> **punctuation**: *bool*. If true, it will return texts with punctuation prediction.

To read an audio file as type *bytes* and get audio information at the same time, you can use *wave* module of python.
```python
import wave
with wave.open(AUDIO_FILE, 'rb') as f:
    samprate = f.getframerate()  # get sample rate of the audio
    sampwidth = f.getsampwidth()  # get sample width of the audio
    audio = f.readframes(f.getnframes())  # read audio as bytes
```

*example_single.py* provides an example usage of single-time ASR call. You can refer to it if confusing about single-time call usage.

### Real-time Call

```python
recognizer.start_streaming()  # start streaming mode

while True:
    chunk = wait_for_data_receive()  # Waiting for audio stream receiving

    recognizer.input(chunk)  # input the new data to the recognizer, and recognizer will autoexec real-time ASR logic.

    result = recognizer.result  # get current result
    print(result["text"])
```

*example_streaming.py* provides an example usage of real-time ASR call by simulating real-time audio stream using an audio file. You can refer to it if confusing about real-time call usage.

