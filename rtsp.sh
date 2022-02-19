#!/bin/sh
INTERFACE=$1
if [ -z $INTERFACE ]; then
    exit 1;
fi

PORT=7236
#if [ -n $2 ];then
    #PORT=$2
#fi

rm -f rtsp.pcap

sudo tcpdump -i $INTERFACE -w rtsp.pcap &

echo "interface : $INTERFACE \
      port : $PORT";

sudo dhclient $INTERFACE;

INTERFACE_IP=$(ifconfig $INTERFACE | grep inet | grep -v inet6 | awk '{print $2}')

if [ -z $INTERFACE_IP ]; then
    echo "dhclient failure..."
    exit 1;
else
    echo "interface ip: $INTERFACE_IP";
fi

#gst-launch-1.0 rtspsrc location=rtsp://192.168.49.1:$PORT do-rtcp=false protocols=tcp ! fakesink
#gst-launch-1.0 udpsrc caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)MP2T-ES" multicast-iface=p2p-wlp3s0-0 port=1028 ! .recv_rtp_sink_0 rtpbin name=rtp rtp. ! rtpmp2tdepay ! tsdemux name=demux demux. ! queue2 ! h264parse ! avdec_h264 ! xvimagesink  demux. ! queue2 ! dvdlpcmdec ! playsink
python3 wfd.py $INTERFACE