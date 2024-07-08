# WeNet ASR Server

The server project implements an API service for WeNet ASR model call using gRPC as the service framework.

## Environment Installation

Run the following command to install python packages in a newly created conda environment:

```bash
pip install -r requirements.txt  # Note: run this command in wenet_asr_server directory.
```

The evironment consists of 3 parts:<br>
· evironment required by *WeNet*<br>
· evironment required by *PPASR* punctuation model<br>
· evironment required by *gRPC* framework

You can refer to the following resources if having problems installing environment.<br>
[WeNet](https://github.com/wenet-e2e/wenet) - official github page<br>
[给语音识别文本加上标点符号](https://blog.csdn.net/qq_33200967/article/details/122474859) - CSDN blog<br>
[PPASR](https://github.com/yeyupiaoling/PPASR) - official github page<br>
[PaddleSpeech](https://github.com/PaddlePaddle/PaddleSpeech) - official github page

<!-- 
### Install python packages for WeNet

Please follow the instructions provided in 

### Install python packages for punctuation model (PaddleSpeech)

Firstly, install *paddlepaddle 2.5.1* package following the **Installation** part of instructions provided in .

```bash
pip install paddlepaddle -i https://mirror.baidu.com/pypi/simple
```

Then install the *ppasr* package using command:

```bash
python -m pip install paddlenlp -i https://mirrors.aliyun.com/pypi/simple/
python -m pip install ppasr -i https://mirrors.aliyun.com/pypi/simple/ -U
```
 -->

## Service Running

```bash
python main.py \
    --model <path to your wenet model if pre-downloaded> \
    --pun-model <path to your punctuation model if pre-downloaded> \
    --hotwords <path to your hotwords dict file if have one> \
    --context-score <float number> \
    --port <port>
```

Command line arguments of *main.py*:

>--model: If you have downloaded a WeNet model before, you can configure it with this argument. If not configured, the WeNet model will be auto-downloaded.
>
>--pun-model: If you have downloaded a PPASR punctuation model before, you can configure it with this argument. If not configured, the PPASR punctuation model will be auto-downloaded. You can download the model [here](https://download.csdn.net/download/qq_33200967/75664996) manually.
>
>--hotwords: You can configure a path to a *.txt* file in which each line records a hotword. The hotword is more probably recognized by WeNet model. See details of the hotword mechanism in the [official documents of WeNet.](https://wenet.org.cn/wenet/context.html)
>
>--context-score: Additional score of each character in a hotword when processing beam-search. 3.0 by default. See details of the hotword mechanism in the [official documents of WeNet.](https://wenet.org.cn/wenet/context.html)
>
>--port: Port of the service process. 50051 by default.
