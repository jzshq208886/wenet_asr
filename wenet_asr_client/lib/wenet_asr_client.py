import grpc

from lib import wenet_asr_pb2
from lib import wenet_asr_pb2_grpc


class Recognizer:
    def __init__(self, sample_rate: int,
                 bit_depth: int = 16,
                 update_duration: int = 10, 
                 puncting_len: int = 40) -> None:
        '''
        初始化音频相关参数。仅支持单声道，故不设channels参数。

        Parameters:
        sample_rate (int): 音频数据采样率。
        bit_depth (int): 音频数据位深度。
        update_duration (int): 更新currentSession间隔。用于伪流式逻辑。
        puncting_len: (int): puncting的自动更新长度。用于流式识别时的标点预测。

        '''

        # self.config = wenet_asr_pb2.RecognitionConfig(
        #     sample_rate_hertz=sample_rate,
        # )
        self.sample_rate = sample_rate
        self.sampwidth = bit_depth / 8 if bit_depth else None
        self.update_duration = update_duration

        self.connected = False
        self.channel = None
        self.stub: wenet_asr_pb2_grpc.WenetASRStub = None

        self.streaming = False
        self.datastream = []
        self.currentSession = b''
        self.fixed = ''
        self.new = ''

        self.punctuation = True
        self.puncting = ''
        self.puncted = ''
        self.puncted_temp = ''
        self.puncfixed = ''
        self.puncting_len = puncting_len

    @property
    def config(self):
        return wenet_asr_pb2.RecognitionConfig(
            sample_rate_hertz=self.sample_rate,
        )

    @property
    def result(self):
        if self.punctuation:
            return {
                'fixed': self.puncfixed,
                'puncted': self.puncted,
                'new': self.new,
                'text': self.puncfixed + self.puncted + self.new,
            }
        return {
            'fixed': self.fixed,
            'puncted': self.puncfixed + self.puncted,
            'new': self.new,
            'text': self.fixed + self.new
        }

    # Build connection between client and server.
    def connect(self, server_port) -> None:
        try:
            self.channel = grpc.insecure_channel(server_port)
            self.stub = wenet_asr_pb2_grpc.WenetASRStub(self.channel)
            self.connected = True
            print(f'Server ID: {self.stub.GetServerID(wenet_asr_pb2.Empty()).text}')
        except Exception as e:
            raise Exception(f'Error connecting to server {server_port}: {e}')

    # Stop the connection between client and server.
    def disconnect(self) -> None:
        self.connected = False
        self.stub = None
        self.channel = None
    
    def start_streaming(self, punctuation=True):
        self.streaming = True
        self.punctuation = punctuation

    def stop_streaming(self):
        self.streaming = False

    def reload_model(self,
                     asr: bool = True,
                     model: str = 'chinese',
                     hotwords: str = None,
                     context_score: int = 3,
                     punctuation: bool = False,
                     punc_model: str = 'pun_models'):
        '''
        重新加载模型。

        参数:
        asr (bool): 是否重新加载asr模型。
        model (str): 所要加载的asr模型。
        hotwords (str): asr模型所要加载的热词增强文件。
        context_score (int): 热词增强中每个字的分数。
        punctuation (bool): 是否重新加载标点符号预测模型。
        punc_model (str): 所要加载的标点符号预测模型。

        '''
        self.stub.ReloadModel(wenet_asr_pb2.ReloadModelRequest(asr=asr,
                                                               model=model,
                                                               hotwords='None' if hotwords is None else hotwords,
                                                               context_score=context_score,
                                                               punctuation=punctuation,
                                                               punctuation_model=punc_model))

    # Upload a new frame of data to server (and trigger recognition logic if streaming).
    def input(self, data: bytes) -> None:
        '''
        将一段数据加入currentSession尾部。流式识别情况下，加入新数据后自动执行伪流式逻辑。

        Parameters:
        data (bytes): 待加入的音频数据。

        '''
        self.datastream.append(data)
        self.currentSession += data

        # 伪流式逻辑
        if self.streaming:
            self.new = self.recognize()
            # 实时添加标点
            if self.punctuation and len(self.puncting + self.new):
                self.puncted = self.punct(self.puncting + self.new)[:-1]
            
            if len(self.currentSession) / self.sampwidth / self.sample_rate > self.update_duration:  # / self.channels
                self.fixed += self.new
                self.puncting += self.new
                
                # 固定化标点
                if self.punctuation:
                    # self.puncted = self.punct()
                    if len(self.puncting) > self.puncting_len:
                        self.puncfixed += self.punct(self.puncting)[:-1]
                        self.puncted = ''
                        self.puncting = ''

                self.new = ''
                self.currentSession = b''

    
    # Conduct recognition logic.
    def recognize(self, data=None, punctuation=False) -> str:
        '''
        对输入音频执行单次语音识别。

        Parameters:
        data (bytes): 输入音频数据。如果不传入数据（如流式识别使用input函数情况下），则默认使用currentSession中的数据。
        punctuation (bool): 用于非流式识别时指定是否同时进行标点预测。

        Returns:
        str: 单次识别结果。

        '''
        if data is None:
            data = self.currentSession
        if not len(data):
            return ''
        text = self.stub.Recognize(wenet_asr_pb2.RecognizeRequest(config=self.config, data=data)).transcript
        if punctuation:
            return self.stub.Punct(wenet_asr_pb2.TextMessage(text=text)).text
        return text
    
    def punct(self, text=None) -> str:
        '''
        对无标点文本执行标点预测。

        Parameters:
        text (string): 无标点文本。若不输入文本，则默认使用puncting文本。

        Returns:
        str: 标点预测后文本。

        '''
        if text is None:
            text = self.puncting
        if not len(text):
            return ''
        return self.stub.Punct(wenet_asr_pb2.TextMessage(text=text)).text
        

