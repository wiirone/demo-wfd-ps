#!/bin/sh

sudo systemctl stop wpa_supplicant.service

sudo ./wpa_supplicant -B -ddd -i wlp3s0 -Dnl80211 -c ../config/wpa_supplicant.conf

sudo wpa_cli interface p2p-dev-wlp3s0

sudo wpa_cli wfd_subelem_set 0 00060011111c0006