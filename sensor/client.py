# python3
from __future__ import absolute_import, division, print_function, unicode_literals
from sensor.pyimagesearch.facedetector import FaceDetector
from sensor.pyimagesearch import imutils
from picamera.array import PiRGBArray
from picamera import PiCamera
from collections import deque
from functools import reduce
import math
import argparse
import time
import cv2
import paho.mqtt.client as mqtt
import time
import thread

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
    testy = abs(sliding_average(q) - 0.5) < 0.1
    print('Avg is ' + sliding_average(q) + ' with condition value: ' + testy)
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
        self.__publish_name = 'TUE/Room-'+ room +'/Sensor/Sensor-Device-'+group_num+'-'+sensor_device_num+'/State'
        # self.__broker_address = "iot.eclipse.org"
        self.client = mqtt.Client("P1")
        self.loop_flag_connected = False
        self.sensor_state = 'OCCUPIED'
        self.launch_thread = True
        sliding_init()


    # The callback for when the client receives a CONNACK response from the server.
    def on_connect(self, client, userdata, flags, rc):
        # global loop_flag_connect
        m = "Connected flags" + str(flags) + "result code " \
            + str(rc) + "client1_id  " + str(client)
        print(m)
        self.loop_flag_connected = True

    # The callback for when a PUBLISH message is received from the server.
    def on_message(self, client1, userdata, message):
        print("message received  ", str(message.payload.decode("utf-8")))

    def send_message(self):
        print('Sending message:')
        # client1.publish("TUE/Room-1/Sensor/Sensor-Device-1-1/State", "Occupied")

    def on_log(self, client, userdata, level, buf):
        print("log: ", buf)

    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: " + str(mid) + " " + str(granted_qos))

    def connect_to_broker(self, broker_address, port, keepalive=60):
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


        # while True:
        #     self.publish('Free')
        #     time.sleep(5)
        self.run_cam()

        # self.client.subscribe("house/bulbs/bulb1")
        # self.client.publish("TUE/Room-1/Sensor/Sensor-Device-1-1/State", "Occupied")
        # time.sleep(5)
        # self.client.loop_forever()
        # client.disconnect()
        self.client.loop_stop()

    def subscribe(self):
        self.client.subscribe("house/bulbs/bulb1")

    def publish(self, msg):
        self.client.publish(self.__publish_name, msg)

    def report_each_5_sec(self):
        while 1:
            # self.publish(self.sensor_state)
            # print(sliding_average(q))
            # print(q)
            # print(sliding_check())
            self.sensor_state = sliding_check()
            self.publish(self.sensor_state)
            # if window_ready():
            time.sleep(5)

    def handle_cam_detection(self, num_faces_detected):
        if self.launch_thread:
            self.launch_thread = False
            thread.start_new_thread(self.report_each_5_sec, ())

        if num_faces_detected > 0:
            # self.sensor_state = 'OCCUPIED'
            # print(num_faces_detected)
            add_to_window(1)
        else:
            # print(num_faces_detected)
            # self.sensor_state = 'FREE'
            add_to_window(0)

        #if the average of queue higher than .6 or lower .4 publish value


        # time.sleep(5)



    def run_cam(self):
        # construct the argument parse and parse the arguments
        ap = argparse.ArgumentParser()
        ap.add_argument("-f", "--face",  # required = True,
                        help="path to where the face cascade resides")
        ap.add_argument("-v", "--video",
                        help="path to the (optional) video file")
        args = vars(ap.parse_args())
        dict_face = {'video': None, 'face': 'sensor/cascades/haarcascade_frontalface_default.xml'}
        # print('Type: ', type(args))
        # print('Args has: ', args)

        # initialize the camera and grab a reference to the raw camera
        # capture
        camera = PiCamera()
        camera.resolution = (640, 480)
        camera.framerate = 32
        rawCapture = PiRGBArray(camera, size=(640, 480))

        # construct the face detector and allow the camera to warm
        # up
        # fd = FaceDetector(args["face"])
        fd = FaceDetector(dict_face["face"])
        time.sleep(0.1)

        # capture frames from the camera
        for f in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image
            frame = f.array

            # resize the frame and convert it to grayscale
            frame = imutils.resize(frame, width=300)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # detect faces in the image and then clone the frame
            # so that we can draw on it
            faceRects = fd.detect(gray, scaleFactor=1.1, minNeighbors=5,
                                  minSize=(30, 30))
            frameClone = frame.copy()

            # for x in faceRects:
            #     print(len(faceRects))

            self.handle_cam_detection(len(faceRects))
            # if len(faceRects) > 0:
            #     # self.face_detected = True
            #     self.publish('Occupied')
            # else:
            #     # self.face_detected = False
            #     self.publish('Free')

            # loop over the face bounding boxes and draw them
            for (fX, fY, fW, fH) in faceRects:
                cv2.rectangle(frameClone, (fX, fY), (fX + fW, fY + fH), (0, 255, 0), 2)

            # show our detected faces, then clear the frame in
            # preparation for the next frame
            cv2.imshow("Face", frameClone)
            rawCapture.truncate(0)

            # if the 'q' key is pressed, stop the loop
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break


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
