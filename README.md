# WeNet ASR Demo

The project inplements an Automatic Speech Recognition (ASR) service based on WeNet model. The project consists of two subprojects, that are WeNet ASR Server project and WeNet ASR Client project.

Here is the [official github page of WeNet project](https://github.com/wenet-e2e/wenet).

## WeNet ASR Server Project

The server project implements a remote API service for WeNet ASR model call using gRPC framework. The project directory is *wenet_asr_server*. Please refer to *wenet_asr_server/README.md* for more information.

## WeNet ASR Client Project

The client project provides python API implemented by a python class. The API encapsulates systematic usage of the remote API service provided by **WeNet ASR Server**. The API not only supports single-time model call, but also provides a real-time ASR calling method. The project directory is *wenet_asr_client*. Please refer to *wenet_asr_client/README.md* for more information.

## GRPC Message Prototype

The *protos* directory defines the gRPC services and messages using Protocol Buffers. The *.proto* file is already compiled to generate python code and the code is adjusted to fit into the project, so you don't need to do it again by yourself.
