# python3
from __future__ import absolute_import, division, print_function, unicode_literals
# from pyimagesearch.facedetector import FaceDetector
# from pyimagesearch import imutils
# from picamera.array import PiRGBArray
# from picamera import PiCamera
from collections import deque
from functools import reduce
# from general import WakaamaProc
from general.WakaamaProc import *
from general import ownership
import math
import argparse
import time
# import cv2
import paho.mqtt.client as mqtt
import time
import thread
import re


q = deque()
Q_SIZE = 10
rdy_to_publish = False

def sliding_init():
    for x in range(Q_SIZE):
        q.append(0.5)

def sliding_average(q):
    try:
        return reduce(lambda x,y: x+y, q) / len(q)
    except:
        return 0.0

def window_ready():
    if abs(sliding_average(q) - 0.5) < 0.1: #not ready
        rdy_to_publish = False
    else:
        rdy_to_publish = True
    return rdy_to_publish

def add_to_window(element):
    q.append(element)
    q.popleft()

def sliding_check():
    if sliding_average(q) > 0.5:
        return "OCCUPIED"
    else:
        return "FREE"

#starts session with broker and publish the message given
class pahoHandler:
    def __init__(self, room = '1', group_num = '31', sensor_device_num = '1'):
        # self.__publish_name = 'TUE/Room-'+ room +'/Sensor/Sensor-Device-'+group_num+'-'+sensor_device_num+'/State'
        # self.__broker_address = "iot.eclipse.org"
        self.__subscribe_text = 'TUE/Room-1/Sensor/+/State'
        self.client = mqtt.Client("P_Light")
        self.loop_flag_connected = False
        self.sensor_state = 'OCCUPIED'
        self.launch_thread = True
        sliding_init()
        self.occupied_workers = ['Sensor-Device-B-1']
        self.run_once_flag = True


    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        # global loop_flag_connect
        m = "Connected flags" + str(flags) + "result code " \
            + str(rc) + "client1_id  " + str(client)
        print(m)
        self.loop_flag_connected = True

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client, userdata, message):
        def get_name(x): return x.split('/')[3]

        sender_device_id = get_name(str(message.topic.decode("utf-8")))
        sender_msg = str(message.payload.decode("utf-8"))
        if sender_msg == 'FREE' and sender_device_id in self.occupied_workers:
            self.occupied_workers.remove(sender_device_id)
            self.state_logic()
        elif sender_msg == 'OCCUPIED' and sender_device_id not in self.occupied_workers:
            self.occupied_workers.append(sender_device_id)
            self.state_logic()
        print('WORKERS____,  ', self.occupied_workers)

    def state_logic(self):
        # while self.run_once_flag:
        print('STATE LOGIC ENTERED')
        person_found = False
        user = None
        # print(self.waka_client.get_persons())
        for p in self.waka_client.get_persons():
            if p.user_type == "USER1" and p.sensor_id in self.occupied_workers:
                user = p.user_id
                person_found = True
                break

        if not person_found:
            for p in self.waka_client.get_persons():
                if p.user_type == "USER2" and p.sensor_id in self.occupied_workers:
                    user = p.user_id
                    person_found = True
                    break

        if not person_found:
            for p in self.waka_client.get_persons():
                if p.user_type == "USER3" and p.sensor_id in self.occupied_workers:
                    user = p.user_id
                    person_found = True
                    break

        if person_found:
            self.waka_client.Load_New_User(user)
        else:
            if len(self.occupied_workers) > 0:
                self.waka_client.Free_Sensor_State(room_empty=False)
            else:
                self.waka_client.Free_Sensor_State(room_empty=True)
                                # self.run_once_flag = not self.run_once_flag

    def send_message(self):
        print('Sending message:')
        # client1.publish("TUE/Room-1/Sensor/Sensor-Device-1-1/State", "Occupied")

    def on_log(self, client, userdata, level, buf):
        print("log11: ", buf)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def connect_to_broker(self, broker_address, port, keepalive=60):
        #start Wakama section
        self.waka_client = Wakaama_Light(broker_address)

        # client = mqtt.Client("P1")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_log = self.on_log
        self.client.on_subscribe = self.on_subscribe
        # time.sleep(1)
        # self.client.connect(broker_address, 1883, 60)
        self.client.connect(broker_address, port, keepalive)
        self.client.loop_start()
        # time.sleep(1)

        # Waits for connection to establish
        self.loop_flag_connected = False
        while not self.loop_flag_connected :
            print('Waiting for connection')
            time.sleep(1)

        # self.client.subscribe("house/bulbs/bulb1")
        self.subscribe()


        #todo thread running
        thread.start_new_thread(self.waka_client.Main_Client_Process, ())


        while True:
            time.sleep(5)

        # while True:
        #     self.publish('Free')
        #     time.sleep(5)
        # self.run_cam()

        # self.client.subscribe("house/bulbs/bulb1")
        # self.client.publish("TUE/Room-1/Sensor/Sensor-Device-1-1/State", "Occupied")
        # time.sleep(5)
        # self.client.loop_forever()
        # client.disconnect()
        self.client.loop_stop()

    def subscribe(self):
        self.client.subscribe(self.__subscribe_text)

    # def publish(self, msg):
    #     self.client.publish(self.__publish_name, msg)

    # def report_each_5_sec(self):
    #     while 1:
    #         # self.publish(self.sensor_state)
    #         # print(sliding_average(q))
    #         # print(q)
    #         # print(sliding_check())
    #         self.sensor_state = sliding_check()
    #         self.publish(self.sensor_state)
    #         time.sleep(5)

    # def handle_cam_detection(self, num_faces_detected):
    #     if self.launch_thread:
    #         self.launch_thread = False
    #         thread.start_new_thread(self.report_each_5_sec, ())

    #     if num_faces_detected > 0:
    #         # self.sensor_state = 'OCCUPIED'
    #         # print(num_faces_detected)
    #         add_to_window(1)
    #     else:
    #         # print(num_faces_detected)
    #         # self.sensor_state = 'FREE'
    #         add_to_window(0)

        #if the average of queue higher than .6 or lower .4 publish value


        # time.sleep(5)



    # def run_cam(self):
    #     # construct the argument parse and parse the arguments
    #     ap = argparse.ArgumentParser()
    #     ap.add_argument("-f", "--face",  # required = True,
    #                     help="path to where the face cascade resides")
    #     ap.add_argument("-v", "--video",
    #                     help="path to the (optional) video file")
    #     args = vars(ap.parse_args())
    #     dict_face = {'video': None, 'face': 'cascades/haarcascade_frontalface_default.xml'}
    #     # print('Type: ', type(args))
    #     # print('Args has: ', args)

    #     # initialize the camera and grab a reference to the raw camera
    #     # capture
    #     camera = PiCamera()
    #     camera.resolution = (640, 480)
    #     camera.framerate = 32
    #     rawCapture = PiRGBArray(camera, size=(640, 480))

    #     # construct the face detector and allow the camera to warm
    #     # up
    #     # fd = FaceDetector(args["face"])
    #     fd = FaceDetector(dict_face["face"])
    #     time.sleep(0.1)

    #     # capture frames from the camera
    #     for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    #         # grab the raw NumPy array representing the image
    #         frame = f.array

    #         # resize the frame and convert it to grayscale
    #         frame = imutils.resize(frame, width=300)
    #         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #         # detect faces in the image and then clone the frame
    #         # so that we can draw on it
    #         faceRects = fd.detect(gray, scaleFactor=1.1, minNeighbors=5,
    #                               minSize=(30, 30))
    #         frameClone = frame.copy()

    #         # for x in faceRects:
    #         #     print(len(faceRects))

    #         self.handle_cam_detection(len(faceRects))
    #         # if len(faceRects) > 0:
    #         #     # self.face_detected = True
    #         #     self.publish('Occupied')
    #         # else:
    #         #     # self.face_detected = False
    #         #     self.publish('Free')

    #         # loop over the face bounding boxes and draw them
    #         for (fX, fY, fW, fH) in faceRects:
    #             cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH), (0, 255, 0), 2)

    #         # show our detected faces, then clear the frame in
    #         # preparation for the next frame
    #         cv2.imshow("Face", frameClone)
    #         rawCapture.truncate(0)

    #         # if the 'q' key is pressed, stop the loop
    #         if cv2.waitKey(1) & 0xFF == ord("q"):
    #             break


# if __name__ == '__main__':
#     BROKER_ADDRESS = "iot.eclipse.org"
#     ph = pahoHandler()
#     ph.connect_to_broker(BROKER_ADDRESS)
    # ph.subscribe()
    # ph.publish('Free')


#client.connect("iot.eclipse.org", 1883, 60)
#broker_address="192.168.1.184"

# broker_address="iot.eclipse.org"
# client1 = mqtt.Client("P1")
# client1.on_connect= on_connect
# client1.on_message=on_message

# time.sleep(1)
#
# client1.connect(broker_address, 1883, 60)
# client1.loop_start()
# client1.subscribe("house/bulbs/bulb1")
# client1.publish("TUE/Room-1/Sensor/Sensor-Device-1-1/State","Occupied")
#
# time.sleep(5)
#
# client1.disconnect()
# client1.loop_stop()
