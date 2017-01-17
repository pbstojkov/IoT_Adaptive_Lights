import sys, os, time
import subprocess
import re
from sense_hat import SenseHat
from evdev import InputDevice, list_devices, ecodes
# from nbstreamreader import NonBlockingStreamReader as NBSR
import ownership
import light
# from Error import *

sensor_clientPath = "general/sensor_lwm2mclient"
light_clientPath = "general/light_lwm2mclient"

#Constants
INIT_RATE = 0.01

#Search constants
SEARCH_LIGHT_STATE = '[light_state]'
SEARCH_SENSOR_STATE = '[sensor_state]'
SEARCH_USER_TYPE = '[user_type]'
SEARCH_USER_ID = '[user_id]'
SEARCH_LIGHT_COLOR = '[light_color]'
SEARCH_LOW_LIGHT = '[low_light]'
SEARCH_GROUP_NO = '[group_no]'
SEARCH_LOCATION_X = '[location_x]'
SEARCH_LOCATION_Y = '[location_y]'
SEARCH_ROOM_ID = '[room_id]'
SEARCH_BEHAVIOR_DEPLOYMENT = '[behavior_deployment]'
SEARCH_OWNERSHIP = '[ownership_priority]'
SEARCH_LIGHT_BEHAVIOR = '[light_behavior]'

#String definitions
OCCUPIED = "OCCUPIED"
FREE = 'FREE'
USED = 'USED'

#Resource IDs
LIGHT_STATE = "/10250/0/2"
USER_TYPE = "/10250/0/3"
USER_ID = "/10250/0/4"
LIGHT_COLOR = "/10250/0/5"
LOW_LIGHT = "/10250/0/6"
GROUP_NO = "/10250/0/7"
LOCATION_X = "/10250/0/8"
LOCATION_Y = "/10250/0/9"
ROOM_ID = "/10250/0/10"
BEHAVIOR_DEPLOYMENT = "/10250/0/11"
OWNERSHIP_PRIORITY = "/10250/0/12"
LIGHT_BEHAVIOR = "/10250/0/13"

SENSOR_STATE = "/10350/0/2"
SENSOR_USER_ID = "/10350/0/3"
SENSOR_GROUP_NO = "/10350/0/4"
SENSOR_LOCATION_X = "/10350/0/5"
SENSOR_LOCATION_Y = "/10350/0/6"
SENSOR_ROOM_ID = "/10350/0/7"


class Wakaama_Sensor():
    def __init__(self, host):
        self.__host = host
        self.__InitSuccess = False
        self.__Exit = False
        self.__sensor_state = FREE
        self.__group_no = 31
        self.__location_x = 0.0
        self.__location_y = 0.0
        self.__room_id = ""


    def __Start_Client_Process(self):
        print self.__host
        
        try:
            self.__cProc = subprocess.Popen([sensor_clientPath,"-h",str(self.__host)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        except:
            return False

        # self.__input = self.__cProc.stdin
        # self.__stdout = NBSR(self.__cProc.stdout)       
        # print Error.ClientInitSuccess
        time.sleep(2)
        return True

    def Main_Client_Process(self):

        if not self.__Start_Client_Process():
            return False

        # while not self.__Exit:
        # for line in iter(self.__stdout.readline, ""):
        for line in iter(self.__cProc.stdout.readline, ""):           
            __Read_Input_line(line)

        self.__stdout.close()
        return_code = self.__cProc.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def __Read_Input_line(self, line):
        if SEARCH_SENSOR_STATE in line:
            self.__sensor_state = line.split(',')[1]

        elif SEARCH_ROOM_ID in line:
            self.__room_id = line.split(',')[1]

        elif SEARCH_LOCATION_Y in line:
            self.__location_y = float(line.split(',')[1])

        elif SEARCH_LOCATION_X in line:
            self.__location_x = float(line.split(',')[1])

        elif SEARCH_GROUP_NO in line:
            self.__group_no = int(line.split(',')[1])

    def Set_Sensor_State(self, state):
        self.__sensor_state = state 
        if state == FREE: 
            cmd = "change " + SENSOR_STATE + " " + state
            self.__cProc.stdin.write(cmd)
        elif state == OCCUPIED:
            cmd = "change " + SENSOR_STATE + " " + state
            self.__cProc.stdin.write(cmd)

    def Kill_Client_Process(self):
        output = subprocess.check_output(["pkill","sensor_lwm2mclient"])
        print output





class Wakaama_Light:

    def __init__(self, host):
        self.__host = host
        self.__InitSuccess = False
        self.__Exit = False

        self.__light_state = FREE
        self.__user_type = ""
        self.__user_id = ""
        self.__light_color = "(0,0,0)"
        self.__low_light = False
        self.__group_no = 31
        self.__location_x = 0.0
        self.__location_y = 0.0
        self.__room_id = ""

        self.__light = Light()
        self.__persons = Persons() 
        #todo: delete below line, it is just a test !
        self.__persons.load_json('https://iot-test.000webhostapp.com/OwnershipPriority.json')

    def __Start_Client_Process(self):
        print self.__host
        
        try:
            self.__cProc = subprocess.Popen([light_clientPath,"-h",str(self.__host)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        except:
            return False

        # self.__input = self.__cProc.stdin
        self.__stdout = NBSR(self.__cProc.stdout)       
        # print Error.ClientInitSuccess
        time.sleep(2)
        return True

    def Main_Client_Process(self):
        if not self.__Start_Client_Process():
            return False

        for line in iter(self.__cProc.stdout.readline, ""):           
        # for line in iter(self.__stdout.readline, ""):        
            __Read_Input_line(line)

        self.__stdout.close()
        return_code = self.__cProc.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def __Read_Input_line(self, line):
        if SEARCH_LIGHT_COLOR in line:
            colors = line.split(',')
            self.__light.change_color(colors[1][1:], colors[2], colors[3][:-1])

            self.__light_color = colors[1] + ',' + colors[2] + ',' + colors[3]
            
            self.__persons.find_user_id_change_values(self.__user_id, light_color=self.__light_color)

        elif SEARCH_LOW_LIGHT in line:
            ll = line.split(',')[1]
            if "True" in ll:
                self.__low_light = True
            elif "False" in ll:
                self.__low_light = False

            self.__light.low_light(self.__low_light)

            self.__persons.find_user_id_change_values(self.__user_id, low_light=self.__low_light)

        elif SEARCH_OWNERSHIP in line:
            url_ownership = line.split(',')[1]
            self.__persons.load_json(url_ownership)

        elif SEARCH_ROOM_ID in line:
            self.__room_id = line.split(',')[1]

        elif SEARCH_LOCATION_Y in line:
            self.__location_y = float(line.split(',')[1])

        elif SEARCH_LOCATION_X in line:
            self.__location_x = float(line.split(',')[1])

        elif SEARCH_GROUP_NO in line:
            self.__group_no = int(line.split(',')[1])

        elif SEARCH_LIGHT_STATE in line:
            self.__light_state = line.split(',')[1]

        elif SEARCH_USER_TYPE in line:
            self.__user_type = line.split(',')[1]

        elif SEARCH_USER_ID in line:
            self.__user_id = line.split(',')[1]


    def Free_Sensor_State(self):
        self.__light_state = FREE
        cmd = "change " + LIGHT_STATE + " " + FREE
        self.__cProc.stdin.write(cmd)

    def Load_New_User(self, new_user_id):
        for p in self.__persons.get_owners():
            # print(p.user_location_x)
            if new_user_id == p.user_id: # our guy is found
                self.__user_id = new_user_id
                cmd = "change " + USER_ID + " " + new_user_id
                self.__cProc.stdin.write(cmd)

                self.__user_type = p.user_type
                cmd = "change " + USER_TYPE + " " + p.user_type
                self.__cProc.stdin.write(cmd)

                self.__light_color = p.light_color
                cmd = "change " + LIGHT_COLOR + " " + p.light_color
                self.__cProc.stdin.write(cmd)

                self.__low_light = p.low_light
                cmd = "change " + LOW_LIGHT + " " + p.low_light
                self.__cProc.stdin.write(cmd)

                self.__light_state = USED
                cmd = "change " + LIGHT_STATE + " " + USED
                self.__cProc.stdin.write(cmd)

                colors = self.__light_color[1:-1].split(',')
                self.__light.low_light(self.__low_light)                
                self.__light.change_color(colors[0], colors[1], colors[2])
                break

    def Kill_Client_Process(self):
        output = subprocess.check_output(["pkill","light_lwm2mclient"])
        print output
