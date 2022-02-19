# demo-wfd-ps
Demo for Wi-Fi display primary sink

### Dependency ###
- Hardware
    + Intel AC8265 in Lenovo T470p laptop
    + Samsung Galaxy S pad
- System OS
    + Ubuntu 18.04.5 kernel version 5.4
- Software 
    + wpa_supplicant2.6
    + dhcpclient
    + python3
    + gstreamer1.14 
    + bash
### Achievement ###
- Laptop is discoverable as a wfd primary sink and connectable as a p2p device using keypad authentication method.
- It can also be allocated an ipv4 address and has basic capability negotiation with the pad to play the MPEG TS stream in rtp packet.
### Limitation ###
- Only support 640x480x30F H.264 CBP 3.1 and LPCM 44800 stereo codec in the WFA WFD spec
- Various performance issues, audio jerk, latency...
- Complex steps to launch
### Steps ###
    TODO