#!/usr/bin/env bash

if [[ -z "$TEAMNUM" ]]; then
	echo "ERR: No team number provided in env" 1>&2
	exit 1
fi

gst-launch-1.0  v4l2src device=/dev/video0 ! tee name=t t. ! queue \
    ! video/x-raw,framerate=30/1,width=640,height=480,format=I420 \
    ! videoconvert ! omxh264enc ! rtph264pay config-interval=-1 pt=96 \
    ! udpsink host=10.{$teamnum:0:1}.{$teamnum:2:3}.5 port=5800 max-bitrate=2700000 t. ! queue \
    ! video/x-raw,framerate=30/1,width=640,height=480,format=I420 \
    ! videoconvert ! omxh264enc ! rtph264pay config-interval=-1 pt=96 \
    ! udpsink host=0.0.0.0 port=5801 max-bitrate=1500000
