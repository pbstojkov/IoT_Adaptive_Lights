#-------------------------------------------------------------------------------
# File Name : ClientProc.py
# Purpose   : Contains the Client Proc
# Author    : Sri Muthu Narayanan Balasubramanian
# Created   : 8 Jan 2016
# Copyright :
#-------------------------------------------------------------------------------

import sys, os, time
import subprocess
import re
from sense_hat import SenseHat
from evdev import InputDevice, list_devices, ecodes
from nbstreamreader import NonBlockingStreamReader as NBSR
# from Error import *

clientPath = "./lwm2mclient"

#Constants
INIT_RATE = 0.01

#Search constants
SEARCH_GROUP_NO = '[group_no]'
SEARCH_LOCATION_X = '[location_x]'
SEARCH_LOCATION_Y = '[location_y]'
SEARCH_ROOM_ID = '[room_id]'
SEARCH_OWNERSHIP = '[ownership_priority]'


#String definitions
OCCUPIED = "OCCUPIED"
FREE = 'FREE'
USED = 'USED'

#Resource IDs
LIGHT_STATE = "/10250/0/2"
USER_TYPE = "/10250/0/3"
USER_ID = "/10250/0/4"
LGHT_COLOR = "/10250/0/5"
LOW_LIGHT = "/10250/0/6"
GROUP_NO = "/10250/0/7"
LOCATION_X = "/10250/0/8"
LOCATION_Y = "/10250/0/9"
ROOM_ID = "/10250/0/10"
BEHAVIOR_DEPLOYMENT = "/10250/0/11"
OWNERSHIP_PRIORITY = "/10250/0/12"
LIGHT_BEHAVIOR = "/10250/0/13"

SENSOR_STATE = "/10350/0/2"
USER_ID = "/10350/0/3"
GROUP_NO = "/10350/0/4"
LOCATION_X = "/10350/0/5"
LOCATION_Y = "/10350/0/6"
ROOM_ID = "/10350/0/7"


class Wakaama_Sensor():

    def __init__(self, host):
        self.__host = host
        self.__InitSuccess = False
        self.__Exit = False
        self.__sensor_state = FREE
        # self.__persons = Persons() # todo add persons to this.

    # def parse_json:
    #   fill list __persons
    
    # def get_persons(self)
    #   return the list.. or search for the person as a "find person function" ?

    def __Start_Client_Process(self):
        print self.__host
        
        try:
            self.__cProc = subprocess.Popen([clientPath,"-h",str(self.__host)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
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

        # while not self.__Exit:
        for line in iter(self.__stdout.readline, ""):
        # for line in iter(self.__cProc.stdout.readline, ""):           
            __Read_Input(line)

        self.__stdout.close()
        return_code = self.__cProc.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def __Read_Input(self, line):
        if SEARCH_OWNERSHIP in line:
            pass
            # todo do something with this
        elif SEARCH_ROOM_ID in line:
            pass
            #todo this too
        elif SEARCH_LOCATION_Y in line:
            pass
        elif SEARCH_LOCATION_X in line:
            pass
        elif SEARCH_GROUP_NO in line:
            pass

    # def __get_ownership_json(self):
        # ...
        # ...

    # todo do setters for all variables in the class!!!
    # each will not only change the variable but also push it to the wakaama client

    def Set_Sensor_State(self, state):
        self.__sensor_state = state 
        if state == FREE: 
            cmd = "change " + SENSOR_STATE + " " + state
            self.__cProc.stdin.write(cmd)
        elif state == OCCUPIED:
            cmd = "change " + SENSOR_STATE + " " + state
            self.__cProc.stdin.write(cmd)
    # def __Init_Rate(self):

    #   cmd = CHANGE + " " + BILLING_RATE + " " + str(INIT_RATE)
    #   print cmd
    #   self.__cProc.stdin.write(cmd)


    # def __Check_Reservation(self):

    #   cmd = DUMP+" "+PARK_STATE+"\n"
    #   self.__cProc.stdin.write(cmd)
    #   tmp_output = self.__stdout.readline(0.01)
    #   while not tmp_output.isspace():
    #       if tmp_output.find(RESERVED)>=0:
    #           self.__sense.clear(255,165,0)
    #           self.__reserved=True
    #           break
    #       tmp_output = self.__stdout.readline(0.01)


    def Kill_Client_Process(self):
        output = subprocess.check_output(["pkill","lwm2mclient"])
        print output





class Wakaama_Light():

    def __init__(self, host):
        self.__host = host
        self.__InitSuccess = False
        self.__Exit = False

        self.__light_state = FREE
        self.__light_color = "(0,0,0)"
        self.__low_light = False
        self.__user_id = ""
        self.__user_type = ""
        # self.__persons = Persons() # todo add persons to this.

    # def parse_json:
    #   fill list __persons
    
    # def get_persons(self)
    #   return the list.. or search for the person as a "find person function" ?

    def __Start_Client_Process(self):
        print self.__host
        
        try:
            self.__cProc = subprocess.Popen([clientPath,"-h",str(self.__host)],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
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

        # while not self.__Exit:
        for line in iter(self.__stdout.readline, ""):
        # for line in iter(self.__cProc.stdout.readline, ""):           
            __Read_Input(line)

        self.__stdout.close()
        return_code = self.__cProc.wait()
        if return_code:
            raise subprocess.CalledProcessError(return_code, cmd)

    def __Read_Input(self, line):
        if SEARCH_OWNERSHIP in line:
            pass
            # todo do something with this
        elif SEARCH_ROOM_ID in line:
            pass
            #todo this too
        elif SEARCH_LOCATION_Y in line:
            pass
        elif SEARCH_LOCATION_X in line:
            pass
        elif SEARCH_GROUP_NO in line:
            pass

    # def __get_ownership_json(self):
        # ...
        # ...

    # todo do setters for all variables in the class!!!
    # each will not only change the variable but also push it to the wakaama client

    def Set_Sensor_State(self, state):
        self.__light_state = state 
        if state == FREE: 
            cmd = "change " + LIGHT_STATE + " " + state
            self.__cProc.stdin.write(cmd)
        elif state == USED:
            cmd = "change " + LIGHT_STATE + " " + state
            self.__cProc.stdin.write(cmd)
    # def __Init_Rate(self):

    #   cmd = CHANGE + " " + BILLING_RATE + " " + str(INIT_RATE)
    #   print cmd
    #   self.__cProc.stdin.write(cmd)


    # def __Check_Reservation(self):

    #   cmd = DUMP+" "+PARK_STATE+"\n"
    #   self.__cProc.stdin.write(cmd)
    #   tmp_output = self.__stdout.readline(0.01)
    #   while not tmp_output.isspace():
    #       if tmp_output.find(RESERVED)>=0:
    #           self.__sense.clear(255,165,0)
    #           self.__reserved=True
    #           break
    #       tmp_output = self.__stdout.readline(0.01)


    def Kill_Client_Process(self):
        output = subprocess.check_output(["pkill","lwm2mclient"])
        print output
