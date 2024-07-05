import argparse

parser = argparse.ArgumentParser("WeNet model remote calling service")
parser.add_argument("--model", default="")

import os
import os.path as osp
from concurrent import futures
import time
import random
import string
import logging
import grpc
from ppasr.infer_utils.pun_predictor import PunctuationPredictor

import wenet
from lib import wenet_asr_pb2
from lib import wenet_asr_pb2_grpc

from lib import audio_read as ar



_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class WenetASR(wenet_asr_pb2_grpc.WenetASRServicer):
    def __init__(self, model, hotwords=None, punc_model='pun_models'):
        self.id = ''.join(random.choices(string.digits, k=16))

        self.model = None
        self.pun_predictor = None
        if osp.exists(model):
            self.model_dir = model
        elif osp.exists(osp.join('model', 'asr', model)):
            self.model_dir = osp.join('model', 'asr', model)
        else:
            raise FileNotFoundError(f"None of directory {model} or {osp.join('model', 'asr', model)} exists.")
        self.hotwords_dir = hotwords if hotwords is None else os.path.join('hotwords', hotwords)
        self.punc_model_dir = str(os.path.join('models', 'punc', punc_model))

        print(f'server_id: {self.id}')

        print('loading ASR model...')
        print(f'Using hotwords dict: {self.hotwords_dir}')
        self.model = wenet.load_model(
            model_dir=self.model_dir,
            context_path=self.hotwords_dir,
            context_score=3.0,
        )
        print('loading punctuation model...')
        self.pun_predictor = PunctuationPredictor(model_dir=self.punc_model_dir, use_gpu=False)
        print('done')

    def Test(self, request, context):
        return wenet_asr_pb2.TextMessage(text=request.text)

    def GetServerID(self, request, context):
        return wenet_asr_pb2.TextMessage(text=self.id)

    def ReloadModel(self, request, context):
        print(f'\nRequest received: ReloadModel: {request}')
        if request.asr:
            print('reloading ASR model...')
            if request.model == 'default':
                model_dir = self.model_dir
            else:
                model_dir = f'models/asr/{request.model}'
                if not os.path.exists(model_dir):
                    print(f'ASR model {model_dir} not found. Using models/asr/chinese instead.')
                    model_dir = 'models/asr/chinese'
            if request.hotwords == 'None':
                context_path = None
            elif request.hotwords == "default":
                context_path = self.hotwords_dir
            else:
                context_path = f'hotwords/{request.hotwords}'
                if not os.path.exists(context_path):
                    print(f'Hotwords file {context_path} not found.')
                    context_path = None
            self.model = wenet.load_model(
                model_dir=model_dir,
                context_path=context_path,
                context_score=request.context_score,
            )
        if request.punctuation:
            print('reloading ASR model...')
            if request.punctuation_model == "default":
                punc_model_dir = self.punc_model_dir
            else:
                punc_model_dir = f'models/punc/{request.punctuation_model}'
                if not os.path.exists(punc_model_dir):
                    print(f'Punctuation predictor model {punc_model_dir} not found. Using models/punc/pun_models instead.')
                    punc_model_dir = 'models/punc/pun_models'
            self.pun_predictor = PunctuationPredictor(model_dir=punc_model_dir, use_gpu=False)
        print('done')
        return wenet_asr_pb2.Empty()

    def Recognize(self, request, context):
        print(f'\nRequest received: Recognize data with length {len(request.data)}.')
        waveform = ar.bytes2tensor(request.data)
        response = wenet_asr_pb2.RecognizeResponse(
            transcript=self.model.transcribe((waveform, request.config.sample_rate_hertz))['text'],
        )
        print(f'Response: transcript="{response.transcript}"')
        return response

    def StreamingRecognize(self, request_iterator, context):
        for request in request_iterator:
            waveform = ar.bytes2tensor(request.data)
            result = self.model.transcribe((waveform, request.config['sample_rate_hertz']))['text']
            yield wenet_asr_pb2.StreamingRecognizeResponse(transcript=result['text'])
    
    def Punct(self, request, context):
        print(f'\nRequest received: Punct: text={request.text}.')
        response = wenet_asr_pb2.TextMessage(text=self.pun_predictor(request.text))
        print(f'Response: text="{response.text}"')
        return response



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    wenet_asr_pb2_grpc.add_WenetASRServicer_to_server(WenetASR('chinese', 'user_dict.txt'), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    logging.basicConfig()
    serve()
