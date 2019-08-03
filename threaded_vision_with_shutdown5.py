#!/usr/bin/python3
from networktables import NetworkTables
from threading import Thread, Condition
import subprocess
import cv2
import datetime
import time
import os

nt_enabled = True
is_competition = False

tape_lower = (0, 0, 241)
tape_upper = (45, 16, 255)

encoder_min = 10250
encoder_max = 17750

encoder1_min = 30750
encoder1_max = 36000

width = 640
height = 480

# sudo gst-launch-1.0 -v udpsrc port=5800 caps="application/x-rtp,media=(string)video,clock-rate=(int)90000,encoding-name=(string)H264,payload=(int)96" ! rtpjitterbuffer latency=1 ! rtph264depay ! decodebin ! videoconvert ! ximagesink

driverstation ='10.15.11.5'
teamnum = os.environ.get('TEAMNUM', 0000)
if teannum == 0000: #no team number is set in system
    sys.stderr.write('ERR: No team number set in "TEAMNUM" var')
    sys.exit(1)
else:
    ip = 'roborio-%s-frc.local' % teamnum
connection_cond = Condition()
connection_notified = [False]


def distance(x, y):
    x = (width/2) - x
    y = (height/2) - y
    return[x, y]


def connectionlistener(connected, info):
    print(info, '; Connected=%s' % connected)
    with connection_cond:
        connection_notified[0] = True
        connection_cond.notify()


if nt_enabled:
    NetworkTables.initialize(server=ip)
    NetworkTables.addConnectionListener(connectionlistener, immediateNotify=True)

    with connection_cond:
        print("Waiting")
        if not connection_notified[0]:
            connection_cond.wait()

    sd = NetworkTables.getTable('SmartDashboard')
    sd.putValue('pi_connected', 'CONNECTED')


class VideoGet(Thread):

    def __init__(self):
        super(VideoGet, self).__init__()
        timestamp = datetime.datetime.now()
        self.stream = cv2.VideoCapture('udpsrc port=5801 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
        self.writer = cv2.VideoWriter('output%s.avi' % timestamp, cv2.VideoWriter_fourcc(*'MJPG'), 30.0, (int(self.stream.get(3)), int(self.stream.get(4))), True)
        self.writer1 = cv2.VideoWriter('output_%s.avi' % timestamp, cv2.VideoWriter_fourcc(*'MJPG'), 30.0, (int(self.stream.get(3)), int(self.stream.get(4))), True)
        self.grabbed, self.frame = self.stream.read()
        self.stopped = False
        print(self.stream)

    def start(self):
        thread = Thread(target=self.get, args=())
        thread.start()
        return self

    def get(self):
        while not self.stopped:
            self.grabbed, self.frame = self.stream.read()

    def stop(self):
        self.stopped = True


def processvision():

    video_src = VideoGet()
    video_getter = video_src.start()

    while True:
        time.sleep(0.33)
        if nt_enabled:
            encoder = sd.getValue('elevator_encoder', 0)
            current_time = sd.getValue('robot_match_time_remaining', 140)
            if current_time <= 0 and not current_time == -1:
                sd.putValue('pi_connected', 'DISCONNECTED')
                video_getter.writer.release()
                video_getter.writer1.release()
                time.sleep(1)
                subprocess.run(["shutdown", "now"])
        else:
            encoder = 0
        
        frame = video_getter.frame
        grabbed = video_getter.grabbed
        if grabbed:
            video_getter.writer1.write(frame)
            m_large = False
            frame = cv2.flip(frame, -1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            frame = cv2.inRange(frame, tape_lower, tape_upper)
            frame = cv2.medianBlur(frame, 13)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            frame = cv2.convertScaleAbs(frame)
            frame = cv2.Canny(frame, 100, 100)
            frame, contours, hier = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            # ^ if opencv >= 4.0.0 remove frame as findcontours no longer returns it ^

            for i in range(len(contours)):
                cv2.drawContours(frame, contours, i, (255, 0, 0), 2, 8, hier, 0)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
            video_getter.writer.write(frame)
            if encoder < encoder_min or encoder1_min > encoder > encoder_max or encoder > encoder1_max:
                mc = []
                for contour in contours:
                    M = cv2.moments(contour)
                    if M["m00"] == 0:
                        cX, cY = 0, 0
                    else:
                        cX, cY = int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])
                        mc.append([(cX, cY), M["m00"]])  # c = [(coords), area]
                massc = 0
                for idx, i in enumerate(mc):
                    massc += i[1]
                try:
                    massc = massc/len(mc)
                except:
                    massc = 0

                if nt_enabled:
                    if len(mc) == 0:
                        sd.putValue('area1', 0)
                        sd.putValue('area2', 0)
                    sd.putValue('area1', massc)
                    if m_large:
                        sd.putValue('area2', massc)
                    else:
                        sd.putValue('area2', massc)
                cX = 0
                cY = 0
                for idx, i in enumerate(mc):
                    cX += int(i[0][0])
                    cY += int(i[0][1])
                try:
                    cX = cX/len(mc)
                    cY = cY/len(mc)
                except:
                    cX = 0
                    cY = 0
                if nt_enabled:
                    sd.putValue('distanceCenterX', distance(cX, cY)[0])
                    sd.putValue('distanceCenterY', distance(cX, cY)[1])

            else:
                # elev in place that breaks vision
                print('disable vision')
                if nt_enabled:
                    sd.putValue('area1', -1)
                    sd.putValue('area2', -1)
                    sd.putValue('distanceCenterX', 0)
                    sd.putValue('distanceCenterX', 0)

        else:
            print('yeeted')
            if nt_enabled:
                sd.putValue('area1', -1)
                sd.putValue('area2', -1)
                sd.putValue('distanceCenterX', 0)
                sd.putValue('distanceCenterY', 0)


processvision()
