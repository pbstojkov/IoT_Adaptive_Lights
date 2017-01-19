import sys, os, time
import subprocess
import re
from sense_hat import SenseHat
from evdev import InputDevice, list_devices, ecodes
# from nbstreamreader import NonBlockingStreamReader as NBSR
from ownership import *
#from light import *
# from Error import *

sensor_clientPath = "general/sensor_lwm2mclient"
light_clientPath = "general/light_lwm2mclient"

#Constants
INIT_RATE = 0.01

#Search constants
# SEARCH_LIGHT_STATE = '[light_state]'
# SEARCH_SENSOR_STATE = '[sensor_state]'
# SEARCH_USER_TYPE = '[user_type]'
# SEARCH_USER_ID = '[user_id]'
# SEARCH_LIGHT_COLOR = '[light_color]'
# SEARCH_LOW_LIGHT = '[low_light]'
# SEARCH_GROUP_NO = '[group_no]'
# SEARCH_LOCATION_X = '[location_x]'
# SEARCH_LOCATION_Y = '[location_y]'
# SEARCH_ROOM_ID = '[room_id]'
# SEARCH_BEHAVIOR_DEPLOYMENT = '[behavior_deployment]'
# SEARCH_OWNERSHIP = '[ownership_priority]'
# SEARCH_LIGHT_BEHAVIOR = '[light_behavior]'
SEARCH_LIGHT_STATE = "10250.0.2"
SEARCH_USER_TYPE = "10250.0.3"
SEARCH_USER_ID = "10250.0.4"
SEARCH_LIGHT_COLOR = "10250.0.5"
SEARCH_LOW_LIGHT = "10250.0.6"
SEARCH_GROUP_NO = "10250.0.7"
SEARCH_LOCATION_X = "10250.0.8"
SEARCH_LOCATION_Y = "10250.0.9"
SEARCH_ROOM_ID = "10250.0.10"
SEARCH_BEHAVIOR_DEPLOYMENT = "10250.0.11"
SEARCH_OWNERSHIP = "10250.0.12"
SEARCH_LIGHT_BEHAVIOR = "10250.0.13"

SEARCH_SENSOR_STATE = "10350.0.2"
SEARCH_SENSOR_USER_ID = "10350.0.3"
SEARCH_SENSOR_GROUP_NO = "10350.0.4"
SEARCH_SENSOR_LOCATION_X = "10350.0.5"
SEARCH_SENSOR_LOCATION_Y = "10350.0.6"
SEARCH_SENSOR_ROOM_ID = "10350.0.7"

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

        self.__received_bytes_numb = 0
        self.__accumulated_line = ""
        self.__is_write_line = None


    def __Parse_Part_Line(self, line):
        print "Line: [" + line + "]"
        if "bytes received" in line:
            words = line.split(" ")             
            bytes = int(words[words.index("bytes") - 1])                                                         
            self.__received_bytes_numb = bytes
            print "Waiting for " + str(self.__received_bytes_numb) + " bytes."
        elif self.__received_bytes_numb > 0:
            if self.__is_write_line is None:
                tmp = line.split("  ")[0].split(" ")[1]
                if tmp == "03":
                    self.__is_write_line = True
                else:
                    self.__is_write_line = False

            data = line.split("  ")[-1][:-1]
            if ' ' in data[:1]:
                data = data.replace(' ', '')

            self.__accumulated_line += data
            print "Data: " + data
            print "len: + " + str(len(data))
            # print type(data)
            try:
                self.__received_bytes_numb -= len(data)
            except Exception as e:
                self.__received_bytes_numb = 0
                return False
            
            if self.__received_bytes_numb == 0:
                if self.__is_write_line:
                    self.__is_write_line = None
                    return True
                else:
                    self.__is_write_line = None
                    return False
                # return True
        return False

    def __Start_Client_Process(self):
        print self.__host
        
        try:
            # self.__cProc = subprocess.Popen([sensor_clientPath,"-h",str(self.__host)],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
            self.__cProc = subprocess.Popen([sensor_clientPath, "-4" , "-h", self.__host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, universal_newlines=True)
        except:
            return False

        # self.__input = self.__cProc.stdin
        # self.__stdout = NBSR(self.__cProc.stdout)       
        # print Error.ClientInitSuccess
        time.sleep(2)
        return True

    def __WTF(self):
        for stdout_line in iter(self.__cProc.stdout.readline, ""):
            yield stdout_line


    def Main_Client_Process(self):

        if not self.__Start_Client_Process():
            return False

        # while not self.__Exit:
        # for line in iter(self.__stdout.readline, ""):
        # for line in iter(self.__cProc.stdout.readline, ""):           
        #     self.__Read_Input_line(line)

        for line in self.__WTF():
            # bs = self.__cProc.stdout.readline(100)
            # print "bs = {" + bs + "}"
            if self.__Parse_Part_Line(line):
                self.__Read_Input_line(self.__accumulated_line)
                self.__accumulated_line = ""

        #self.__cProc.stdout.close()
        return_code = self.__cProc.wait()
        if return_code:
            print "return code: " + str(return_code)
            #raise subprocess.CalledProcessError(return_code, cmd)

    def __Read_Input_line(self, line):
        if SEARCH_SENSOR_STATE in line:
            self.__sensor_state = line.split(".")[-1] #line.split(',')[1]

            cmd = "change " + SENSOR_STATE + " " + self.__sensor_state
            self.__cProc.stdin.write(cmd)

        elif SEARCH_SENSOR_ROOM_ID in line:
            self.__room_id = line.split(".")[-1] #line.split(',')[1]

            cmd = "change " + SENSOR_ROOM_ID + " " + self.__room_id
            self.__cProc.stdin.write(cmd)

        elif SEARCH_SENSOR_LOCATION_Y in line:
            self.__location_y = float(line.split(".")[-1]) #line.split(',')[1])

            cmd = "change " + SENSOR_LOCATION_Y + " " + str(self.__location_y)
            self.__cProc.stdin.write(cmd)

        elif SEARCH_SENSOR_LOCATION_X in line:
            self.__location_x = float(line.split(".")[-1]) #line.split(',')[1])

            cmd = "change " + SENSOR_LOCATION_X + " " + str(self.__location_x)
            self.__cProc.stdin.write(cmd)

        elif SEARCH_SENSOR_GROUP_NO in line:
            self.__group_no = int(line.split(".")[-1]) #line.split(',')[1])

            cmd = "change " + SENSOR_GROUP_NO + " " + str(self.__group_no)
            self.__cProc.stdin.write(cmd)

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

        self.__received_bytes_numb = 0
        self.__accumulated_line = ""
        self.__is_write_line = None

    def __Parse_Part_Line(self, line):
        print "Line: [" + line + "]"
        if "bytes received" in line:
            words = line.split(" ")
            bytes = int(words[words.index("bytes") - 1])
            self.__received_bytes_numb = bytes
            print "Waiting for " + str(self.__received_bytes_numb) + " bytes."
        elif self.__received_bytes_numb > 0:
            if self.__is_write_line is None:
                tmp = line.split("  ")[0].split(" ")[1]
                if tmp == "03":
                    self.__is_write_line = True
                else:
                    self.__is_write_line = False

            data = line.split("  ")[-1][:-1]
            if ' ' in data[:1]:
                data = data.replace(' ', '')

            self.__accumulated_line += data
            print "Data: " + data
            print "len: + " + str(len(data))
            # print type(data)
            try:
                self.__received_bytes_numb -= len(data)
            except Exception as e:
                self.__received_bytes_numb = 0
                return False
            
            if self.__received_bytes_numb == 0:
                if self.__is_write_line:
                    self.__is_write_line = None
                    return True
                else:
                    self.__is_write_line = None
                    return False
                # return True
        return False

    def __Start_Client_Process(self):
        # print type(self.__host)
        print self.__host
        
        try:
            self.__cProc = subprocess.Popen([light_clientPath, "-4" , "-h", self.__host], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, universal_newlines=True)
        except:
            print "Fail"
            return False

        # self.__input = self.__cProc.stdin
        # self.__stdout = NBSR(self.__cProc.stdout)       
        # print Error.ClientInitSuccess
        time.sleep(2)
        return True

    def __WTF(self):
        for stdout_line in iter(self.__cProc.stdout.readline, ""):
            yield stdout_line

    def Main_Client_Process(self):
        if not self.__Start_Client_Process():
            return False

        # for line in iter(self.__cProc.stdout.readline, ""):           
        # # for line in iter(self.__stdout.readline, ""):        
        #     print("bs" + line)
        #     self.__Read_Input_line(line)

        # while not self.__Exit:
        #     line = self.__cProc.stdout.readline()
        #     # print("bs: " + line)
        #     if line != '':
        #         # print(line)
        #         self.__Read_Input_line(line)

        for line in self.__WTF():
            # bs = self.__cProc.stdout.readline(100)
            # print "bs = {" + bs + "}"
            if self.__Parse_Part_Line(line):
                self.__Read_Input_line(self.__accumulated_line)
                self.__accumulated_line = ""

        print("WTF!?!?!?")
        # self.__cProc.stdout.close()
        return_code = self.__cProc.wait()
        if return_code:
            print(return_code)
            return False
            # raise subprocess.CalledProcessError(return_code, cmd)

    def __Read_Input_line(self, line):
        print "reading . [" + line + "]"
        if SEARCH_LIGHT_COLOR in line:
            # colors = line.split(',')
            colors_str = line.split(".")[-1]
            colors = colors_str[1:-1].split(',')
            self.__light.change_color(colors[0], colors[1], colors[2])

            self.__light_color = colors_str
            
            self.__persons.find_user_id_change_values(self.__user_id, light_color=self.__light_color)

        elif SEARCH_LOW_LIGHT in line:
            # ll = line.split(',')[1]
            ll = line.split(".")[-1]
            if "True" in ll:
                self.__low_light = True
            elif "False" in ll:
                self.__low_light = False

            self.__light.low_light(self.__low_light)

            self.__persons.find_user_id_change_values(self.__user_id, low_light=self.__low_light)

        elif SEARCH_OWNERSHIP in line:
            # url_ownership = line.split(',')[1]
            url_ownership = line.split(".")[-1]
            self.__persons.load_json(url_ownership)

        elif SEARCH_ROOM_ID in line:
            self.__room_id = line.split(".")[-1] #line.split(',')[1]

        elif SEARCH_LOCATION_Y in line:
            self.__location_y = float(line.split(".")[-1]) #line.split(',')[1])

        elif SEARCH_LOCATION_X in line:
            self.__location_x = float(line.split(".")[-1]) #line.split(',')[1])

        elif SEARCH_GROUP_NO in line:
            self.__group_no = int(line.split(".")[-1]) #line.split(',')[1])

        elif SEARCH_LIGHT_STATE in line:
            self.__light_state = line.split(".")[-1] #line.split(',')[1]

        elif SEARCH_USER_TYPE in line:
            self.__user_type = line.split(".")[-1] #line.split(',')[1]

        elif SEARCH_USER_ID in line:
            self.__user_id = line.split(".")[-1] #line.split(',')[1]


    def Free_Sensor_State(self, room_empty):
        self.__light_state = FREE
        cmd = "change " + LIGHT_STATE + " " + FREE
        self.__cProc.stdin.write(cmd)

        if room_empty:
            off = '(0,0,0)'
            colors = off[1:-1].split(',')
            self.__light.change_color(colors[0], colors[1], colors[2])
            self.__light_color = off
        else:
            dim  = '(250,200,100)'
            colors = dim[1:-1].split(',')
            self.__light.change_color(colors[0], colors[1], colors[2])
            self.__light_color = dim

        cmd = "change " + LIGHT_COLOR + " " + self.__light_color
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
                cmd = "change " + LOW_LIGHT + " " + str(p.low_light)
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

    def get_persons(self):
        return self.__persons.get_owners()


# if __name__ == "__main__":
#     import AvahiDiscovery
#     ROOM = 1
#     BROKER_ADDRESS = AvahiDiscovery.find_broker(ROOM)
#     sensor_clientPath = "./sensor_lwm2mclient"
#     light_clientPath = "./light_lwm2mclient"

#     wc = Wakaama_Light(BROKER_ADDRESS)
#     wc.Main_Client_Process()
