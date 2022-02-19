#!/usr/bin/python3

"WFD implementation in Python3"

import sys

import gi
gi.require_version('GObject','2.0')
gi.require_version('GLib','2.0')
gi.require_version('Gst','1.0')

from gi.repository import Gst,GLib,GObject

from enum import Enum

def get_default_uri():
    return "rtsp://192.168.49.1:7236"

WfdRole = Enum('WfdRole',('Source','Primary_Sink'))
    
WfdVersion = Enum('WfdVersion',('v1','v2'))

import socket
from urllib.parse import urlparse

class Wfd:
    
    "Wi-Fi Display"

    CStartSeq = 1
    has_datatime_hdr = False

    def __init__(self,p2p_interface='lo',server_uri=get_default_uri(),role=WfdRole.Primary_Sink,version=WfdVersion.v1):
        self._p2p_interface = p2p_interface
        print(self._p2p_interface)
        self._server_uri = server_uri
        self._role = role
        self._version = version
        self._CSeq = Wfd.CStartSeq

    @property
    def cseq(self):
        return self._CSeq

    @property
    def server_uri(self):
        return self._server_uri
    
    @property
    def role(self):
        return self._role

    @property
    def version(self):
        return self._version

    def connect(self):
        server = urlparse(self.server_uri)        
        self._rtspSock = socket.socket()
        self._rtspSock.connect((server.hostname,server.port))

    def disconnect(self):
        pass

    def reset(self):
        pass

    def _createPipeline(self):
        Gst.init()
        str =  "udpsrc caps=\"application/x-rtp,media=(string)video,clock-rate=(int)27000000,encoding-name=(string)MP2T-ES\" multicast-iface=%s port=1028 ! .recv_rtp_sink_0 rtpbin name=rtp \
                rtp. ! queue2 ! rtpmp2tdepay ! tsdemux name=demux \
                demux. ! queue2 ! h264parse ! avdec_h264 ! videoconvert ! xvimagesink \
                demux. ! queue2 ! dvdlpcmdec ! playsink".format(self._p2p_interface)
        self.pipeline = Gst.parse_launch(str)
        self.pipeline.set_state(Gst.State.PLAYING)

    def capNegotiation(self):
        state = 0
        while True:
            buffer = []
            d = self._rtspSock.recv(1000)
            if d:
                buffer.append(d)
            else:
                continue
            data = b''.join(buffer)
            print(data.decode())
            if state == 0:
                self._rtspSock.send(self._M1Response(1,200,'ok'))
                self._rtspSock.send(self._M2Request())
                self._CSeq += 1
                state = 1
            elif state == 1:
                state = 2
            elif state == 2:
                self._rtspSock.send(self._M3Response(2,200,'ok'))
                state = 3
            elif state == 3:
                self._rtspSock.send(self._M4Response(3))
                state = 4
            elif state == 4:
                self._rtspSock.send(self._M5Response(4))
                self._rtspSock.send(self._M6Request())
                self._CSeq += 1
                state = 5
            elif state == 5:
                # get rtsp server port and rtp connect
                #self._createPipeline()
                session = data.split(b'\r\n',6)[2]
                if session.decode().startswith('Session:'):
                    print(session.decode())
                    session_tag,session_content = session.split(b' ',2)
                    session_id,timeout = session_content.split(b';',2)
                    self._session_id = session_id.decode()
                    print(self._session_id)
                    self._rtspSock.send(self._M7Request('rtsp://192.168.49.1/wfd1.0/streamid=0',self._session_id))
                    self._createPipeline()
                    state = 6
            elif state == 6:
                pass
        self._rtspSock.close()


    def _M1Request(self):
        pass

    def _M1Response(self,cseq,codeId,codeInfo):
        return f"RTSP/1.0 {codeId} {codeInfo.upper()}\r\nCSeq: {cseq}\r\nPublic: org.wfa.wfd1.0, GET_PARAMETER, SET_PARAMETER\r\n\r\n".encode('utf-8')

    def _M2Request(self):
        return f"OPTIONS * RTSP/1.0\r\nCSeq: {self._CSeq}\r\nRequire: org.wfa.wfd1.0\r\n\r\n".encode('utf-8')

    def _M2Response(self):
        pass

    def _M3Request(self):
        pass

    def _M3Response(self,cseq,codeId,codeInfo):
        
        parameters = "wfd_video_formats: 00 00 01 01 00000001 00000000 00000000 00 0000 0000 00 none none\r\n"
        parameters += "wfd_audio_codecs: LPCM 00000003 00\r\n"
        parameters += "wfd_content_protection: none\r\n"
        parameters += "wfd_client_rtp_ports: RTP/AVP/UDP;unicast 1028 0 mode=play\r\n"
        parameters += "wfd_uibc_capability: none\r\n"
        length = len(parameters)
        str = f"RTSP/1.0 {codeId} {codeInfo.upper()}\r\nCSeq: {cseq}\r\nContent-Length: {length}\r\nContent-Type: text/parameters\r\n\r\n"
        str += parameters
        return str.encode('utf-8')
    
    def _M4Request(self):
        pass

    def _M4Response(self,cseq):
        return self._OkResponse(cseq)

    def _M5Request(self):
        pass

    def _M5Response(self,cseq):
        return self._OkResponse(cseq)

    def _M6Request(self,server_uri='rtsp://192.168.49.1/wfd1.0/streamid=0'):
        return f"SETUP {server_uri} RTSP/1.0\r\nCSeq: {self._CSeq}\r\nTransport: RTP/AVP/UDP;unicast;client_port=1028\r\n\r\n".encode('utf-8')
    
    def _M6Response(self):
        pass

    def _M7Request(self,server_uri='rtsp://192.168.49.1/wfd1.0/streamid=0',session_id='00000000'):
        return f"PLAY {server_uri} RTSP/1.0\r\nCSeq: {self._CSeq}\r\nSession: {session_id}\r\n\r\n".encode('utf-8')
    
    def _M7Response(self,cseq):
        pass
    
    def _M16Response(self,cseq):
        return self._OkResponse(cseq)

    def _OkResponse(self,cseq):
        return f"RTSP/1.0 200 OK\r\nCSeq: {cseq}\r\n\r\n".encode('utf-8')

def main(args):
    w = Wfd(p2p_interface=args[1])
    w.connect()
    w.capNegotiation()

if __name__=='__main__':
    sys.exit(main(sys.argv))