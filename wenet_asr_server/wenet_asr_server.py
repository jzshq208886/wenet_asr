from concurrent import futures
import time
import logging
import grpc
from ppasr.infer_utils.pun_predictor import PunctuationPredictor

import wenet
from lib import wenet_asr_pb2
from lib import wenet_asr_pb2_grpc

from lib import audio_read as ar

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class WenetASR(wenet_asr_pb2_grpc.WenetASRServicer):
    def __init__(self):
        self.model = None
        print('loading model...')
        self.model = wenet.load_model(model_dir='models/chinese')
        self.pun_predictor = PunctuationPredictor(model_dir='models/pun_models', use_gpu=False)
        print('done')

    def Test(self, request, context):
        return wenet_asr_pb2.TextMessage(text=request.text)

    def Recognize(self, request, context):
        waveform = ar.bytes2tensor(request.data)
        return wenet_asr_pb2.RecognizeResponse(
            transcript=self.model.transcribe((waveform, request.config.sample_rate_hertz))['text'],
        )

    def StreamingRecognize(self, request_iterator, context):
        for request in request_iterator:
            waveform = ar.bytes2tensor(request.data)
            result = self.model.transcribe((waveform, request.config['sample_rate_hertz']))['text']
            yield wenet_asr_pb2.StreamingRecognizeResponse(transcript=result['text'])
    
    def Punct(self, request, context):
        return wenet_asr_pb2.TextMessage(text=self.pun_predictor(request.text))



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    wenet_asr_pb2_grpc.add_WenetASRServicer_to_server(WenetASR(), server)
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
