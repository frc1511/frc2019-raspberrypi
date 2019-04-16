#!/usr/bin/env bash

# restart network until gets ip

#while true;
#    do
#        ip=$(hostname -I)
#        if [[ -z "$ip" ]]
#        then
#            ifdown eth0
#            ifup eth0
#        else
#            break
#        fi
#done

# start v4l2loopback to get a second video device (/dev/video1 with one camera)
#sudo modprobe v4l2loopback devices=1

#gst-launch-1.0 v4l2src device=/dev/video0  ! tee name=t \
#    t. ! queue ! video/x-raw,framerate=30/1,width=640,height=480 ! omxh264enc ! rtph264pay config-interval=10 pt=96 \
#       ! udpsink host=10.15.11.6 port=5800 max-bitrate=2700000 \
#    t. ! queue ! v4l2sink device=/dev/video1 &


gst-launch-1.0  v4l2src device=/dev/video0 ! tee name=t t. ! queue \
    ! video/x-raw,framerate=30/1,width=640,height=480,format=I420 \
    ! videoconvert ! omxh264enc ! rtph264pay config-interval=-1 pt=96 \
    ! udpsink host=10.15.11.5 port=5800 max-bitrate=2700000 t. ! queue \
    ! video/x-raw,framerate=30/1,width=640,height=480,format=I420 \
    ! videoconvert ! omxh264enc ! rtph264pay config-interval=-1 pt=96 \
    ! udpsink host=0.0.0.0 port=5801 max-bitrate=1500000

#sleep 4

#python3 threaded_vision_with_shutdown.py &
