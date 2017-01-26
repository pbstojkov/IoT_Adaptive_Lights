/*******************************************************************************
 *
 * Copyright (c) 2013, 2014 Intel Corporation and others.
 * All rights reserved. This program and the accompanying materials
 * are made available under the terms of the Eclipse Public License v1.0
 * and Eclipse Distribution License v1.0 which accompany this distribution.
 *
 * The Eclipse Public License is available at
 *    http://www.eclipse.org/legal/epl-v10.html
 * The Eclipse Distribution License is available at
 *    http://www.eclipse.org/org/documents/edl-v10.php.
 *
 * Contributors:
 *    David Navarro, Intel Corporation - initial API and implementation
 *    domedambrosio - Please refer to git log
 *    Fabien Fleutot - Please refer to git log
 *    Axel Lorente - Please refer to git log
 *    Bosch Software Innovations GmbH - Please refer to git log
 *    Pascal Rieux - Please refer to git log
 *    
 *******************************************************************************/

/*
 Copyright (c) 2013, 2014 Intel Corporation

 Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright notice,
       this list of conditions and the following disclaimer in the documentation
       and/or other materials provided with the distribution.
     * Neither the name of Intel Corporation nor the names of its contributors
       may be used to endorse or promote products derived from this software
       without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
 IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
 INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
 THE POSSIBILITY OF SUCH DAMAGE.

 David Navarro <david.navarro@intel.com>

*/

/*
 * This object is single instance only, and is mandatory to all LWM2M device as it describe the object such as its
 * manufacturer, model, etc...
 */

#include "liblwm2m.h"
#include "lwm2mclient.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>


// #define PRV_MANUFACTURER      "Open Mobile Alliance"
// #define PRV_MODEL_NUMBER      "Lightweight M2M Client"
// #define PRV_SERIAL_NUMBER     "345000123"
// #define PRV_FIRMWARE_VERSION  "1.0"
// #define PRV_POWER_SOURCE_1    1
// #define PRV_POWER_SOURCE_2    5
// #define PRV_POWER_VOLTAGE_1   3800
// #define PRV_POWER_VOLTAGE_2   5000
// #define PRV_POWER_CURRENT_1   125
// #define PRV_POWER_CURRENT_2   900
// #define PRV_BATTERY_LEVEL     100
// #define PRV_MEMORY_FREE       15
// #define PRV_ERROR_CODE        0
// #define PRV_TIME_ZONE         "Europe/Berlin"
// #define PRV_BINDING_MODE      "U"

// #define PRV_OFFSET_MAXLEN   7 //+HH:MM\0 at max
// #define PRV_TLV_BUFFER_SIZE 128

// Resource Id's:

#define RES_0_LIGHT_ID              0
#define RES_0_DEVICE_TYPE           1
#define RES_0_LIGHT_STATE           2
#define RES_0_USER_TYPE             3
#define RES_0_USER_ID               4
#define RES_0_LIGHT_COLOR           5
#define RES_0_LOW_LIGHT             6
#define RES_0_GROUP_NO              7
#define RES_0_LOCATION_X            8
#define RES_0_LOCATION_Y            9
#define RES_0_ROOM_ID               10
#define RES_0_BEHAVIOR_DEPLOYMENT   11
#define RES_0_OWNERSHIP_PRIORITY    12
#define RES_0_LIGHT_BEHAVIOR        13



typedef struct
{
    char LightID[20]; // "Light-Device-31-1"
    char DeviceType[14]; // "Light Device"
    char LightState[5]; // "FREE" or "USED"
    char UserType[10]; // "USERx" 1/2/3
    char UserID[20]; //
    char LightColor[20]; // "(r, g, b)"
    uint8_t LowLight; // boolean
    uint8_t GroupNo; // 31
    float LocationX;
    float LocationY;
    char RoomID[10]; // "Room-1"
    char BehaviorDeployment[15]; // "Broker" or "Distributed"
    char OwnershipPriority[255]; // link to json file on ownership priority
    char LightBehavior[255]; // link to update file
} light_device_data_t;


// // basic check that the time offset value is at ISO 8601 format
// // bug: +12:30 is considered a valid value by this function
// static int prv_check_time_offset(char * buffer,
//                                  int length)
// {
//     int min_index;

//     if (length != 3 && length != 5 && length != 6) return 0;
//     if (buffer[0] != '-' && buffer[0] != '+') return 0;
//     switch (buffer[1])
//     {
//     case '0':
//         if (buffer[2] < '0' || buffer[2] > '9') return 0;
//         break;
//     case '1':
//         if (buffer[2] < '0' || buffer[2] > '2') return 0;
//         break;
//     default:
//         return 0;
//     }
//     switch (length)
//     {
//     case 3:
//         return 1;
//     case 5:
//         min_index = 3;
//         break;
//     case 6:
//         if (buffer[3] != ':') return 0;
//         min_index = 4;
//         break;
//     default:
//         // never happen
//         return 0;
//     }
//     if (buffer[min_index] < '0' || buffer[min_index] > '5') return 0;
//     if (buffer[min_index+1] < '0' || buffer[min_index+1] > '9') return 0;

//     return 1;
// }

// static uint8_t prv_set_value(lwm2m_data_t * dataP,
//                              device_data_t * devDataP)
// {
//     // a simple switch structure is used to respond at the specified resource asked
//     switch (dataP->id)
//     {
//     case RES_O_MANUFACTURER:
//         lwm2m_data_encode_string(PRV_MANUFACTURER, dataP);
//         return COAP_205_CONTENT;

//     case RES_O_MODEL_NUMBER:
//         lwm2m_data_encode_string(PRV_MODEL_NUMBER, dataP);
//         return COAP_205_CONTENT;

//     case RES_O_SERIAL_NUMBER:
//         lwm2m_data_encode_string(PRV_SERIAL_NUMBER, dataP);
//         return COAP_205_CONTENT;

//     case RES_O_FIRMWARE_VERSION:
//         lwm2m_data_encode_string(PRV_FIRMWARE_VERSION, dataP);
//         return COAP_205_CONTENT;

//     case RES_M_REBOOT:
//         return COAP_405_METHOD_NOT_ALLOWED;

//     case RES_O_FACTORY_RESET:
//         return COAP_405_METHOD_NOT_ALLOWED;

//     case RES_O_AVL_POWER_SOURCES: 
//     {
//         lwm2m_data_t * subTlvP;

//         subTlvP = lwm2m_data_new(2);

//         subTlvP[0].id = 0;
//         lwm2m_data_encode_int(PRV_POWER_SOURCE_1, subTlvP);
//         subTlvP[1].id = 1;
//         lwm2m_data_encode_int(PRV_POWER_SOURCE_2, subTlvP + 1);

//         lwm2m_data_encode_instances(subTlvP, 2, dataP);

//         return COAP_205_CONTENT;
//     }

//     case RES_O_POWER_SOURCE_VOLTAGE:
//     {
//         lwm2m_data_t * subTlvP;

//         subTlvP = lwm2m_data_new(2);

//         subTlvP[0].id = 0;
//         lwm2m_data_encode_int(PRV_POWER_VOLTAGE_1, subTlvP);
//         subTlvP[1].id = 1;
//         lwm2m_data_encode_int(PRV_POWER_VOLTAGE_2, subTlvP + 1);

//         lwm2m_data_encode_instances(subTlvP, 2, dataP);

//         return COAP_205_CONTENT;
//     }

//     case RES_O_POWER_SOURCE_CURRENT:
//     {
//         lwm2m_data_t * subTlvP;

//         subTlvP = lwm2m_data_new(2);

//         subTlvP[0].id = 0;
//         lwm2m_data_encode_int(PRV_POWER_CURRENT_1, &subTlvP[0]);
//         subTlvP[1].id = 1;
//         lwm2m_data_encode_int(PRV_POWER_CURRENT_2, &subTlvP[1]);
 
//         lwm2m_data_encode_instances(subTlvP, 2, dataP);

//         return COAP_205_CONTENT;
//     }

//     case RES_O_BATTERY_LEVEL:
//         lwm2m_data_encode_int(devDataP->battery_level, dataP);
//         return COAP_205_CONTENT;

//     case RES_O_MEMORY_FREE:
//         lwm2m_data_encode_int(devDataP->free_memory, dataP);
//         return COAP_205_CONTENT;

//     case RES_M_ERROR_CODE:
//     {
//         lwm2m_data_t * subTlvP;

//         subTlvP = lwm2m_data_new(1);

//         subTlvP[0].id = 0;
//         lwm2m_data_encode_int(devDataP->error, subTlvP);

//         lwm2m_data_encode_instances(subTlvP, 1, dataP);

//         return COAP_205_CONTENT;
//     }        
//     case RES_O_RESET_ERROR_CODE:
//         return COAP_405_METHOD_NOT_ALLOWED;

//     case RES_O_CURRENT_TIME:
//         lwm2m_data_encode_int(time(NULL) + devDataP->time, dataP);
//         return COAP_205_CONTENT;

//     case RES_O_UTC_OFFSET:
//         lwm2m_data_encode_string(devDataP->time_offset, dataP);
//         return COAP_205_CONTENT;

//     case RES_O_TIMEZONE:
//         lwm2m_data_encode_string(PRV_TIME_ZONE, dataP);
//         return COAP_205_CONTENT;
      
//     case RES_M_BINDING_MODES:
//         lwm2m_data_encode_string(PRV_BINDING_MODE, dataP);
//         return COAP_205_CONTENT;

//     default:
//         return COAP_404_NOT_FOUND;
//     }
// }

static uint8_t prv_light_device_read(uint16_t instanceId,
                               int * numDataP,
                               lwm2m_data_t ** dataArrayP,
                               lwm2m_object_t * objectP)
{
    uint8_t result;
    int i;

    light_device_data_t * data = (light_device_data_t*)(objectP->userData);

    // this is a single instance object
    if (instanceId != 0)
    {
        return COAP_404_NOT_FOUND;
    }

    // is the server asking for the full object ?
    if (*numDataP == 0)
    {
        uint16_t resList[] = {
            RES_0_LIGHT_ID,
            RES_0_DEVICE_TYPE,
            RES_0_LIGHT_STATE,
            RES_0_USER_TYPE,
            RES_0_USER_ID,
            RES_0_LIGHT_COLOR,
            RES_0_LOW_LIGHT,
            RES_0_GROUP_NO,
            RES_0_LOCATION_X,
            RES_0_LOCATION_Y,
            RES_0_ROOM_ID,
            RES_0_BEHAVIOR_DEPLOYMENT,
            RES_0_OWNERSHIP_PRIORITY,
            RES_0_LIGHT_BEHAVIOR,
        };
        int nbRes = sizeof(resList)/sizeof(uint16_t);

        *dataArrayP = lwm2m_data_new(nbRes);
        if (*dataArrayP == NULL) return COAP_500_INTERNAL_SERVER_ERROR;
        *numDataP = nbRes;
        for (i = 0 ; i < nbRes ; i++)
        {
            (*dataArrayP)[i].id = resList[i];
        }
    }

    i = 0;
    do
    {
        switch ((*dataArrayP)[i].id)
        {
        case RES_0_LIGHT_ID:
            lwm2m_data_encode_string((uint8_t*)data->LightID, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (uint8_t *)lwm2m_malloc(20);  
            // strncpy((*dataArrayP)[i].value, (uint8_t*)data->LightID, 20);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 20;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_DEVICE_TYPE:
            lwm2m_data_encode_string((uint8_t*)data->DeviceType, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (char *)lwm2m_malloc(14);  
            // strncpy((*dataArrayP)[i].value, (char*)data->DeviceType, 14);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 14;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_LIGHT_STATE:
            lwm2m_data_encode_string((uint8_t*)data->LightState, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (char *)lwm2m_malloc(5);  
            // strncpy((*dataArrayP)[i].value, (char*)data->LightState, 5);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 5;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_USER_TYPE:
            lwm2m_data_encode_string((uint8_t*)data->UserType, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (char *)lwm2m_malloc(10);  
            // strncpy((*dataArrayP)[i].value, (char*)data->UserType, 10);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 10;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_USER_ID:
            lwm2m_data_encode_string((uint8_t*)data->UserID, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (char *)lwm2m_malloc(20);  
            // strncpy((*dataArrayP)[i].value, (char*)data->UserID, 20);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 20;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_LIGHT_COLOR:
            lwm2m_data_encode_string((uint8_t*)data->LightColor, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (char *)lwm2m_malloc(20);  
            // strncpy((*dataArrayP)[i].value, (char*)data->LightColor, 20);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 20;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_LOW_LIGHT:
            lwm2m_data_encode_int(data->LowLight, *dataArrayP + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_INTEGER;
            // (*dataArrayP)[i].length = 20;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_GROUP_NO:
            lwm2m_data_encode_int(data->GroupNo, *dataArrayP + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_INTEGER;
            // (*dataArrayP)[i].length = 20;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_LOCATION_X:
            lwm2m_data_encode_float(data->LocationX, *dataArrayP + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_FLOAT;
            // (*dataArrayP)[i].length = 20;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_LOCATION_Y:
            lwm2m_data_encode_float(data->LocationY, *dataArrayP + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_FLOAT;
            // (*dataArrayP)[i].length = 20;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_ROOM_ID:
            lwm2m_data_encode_string((uint8_t*)data->RoomID, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (char *)lwm2m_malloc(10);  
            // strncpy((*dataArrayP)[i].value, (char*)data->RoomID, 10);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 10;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        case RES_0_BEHAVIOR_DEPLOYMENT:
            lwm2m_data_encode_string((uint8_t*)data->BehaviorDeployment, (*dataArrayP) + i);
            result = COAP_205_CONTENT;
            // (*dataArrayP)[i].value =  (char *)lwm2m_malloc(15);  
            // strncpy((*dataArrayP)[i].value, (char*)data->BehaviorDeployment, 15);           
            // (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
            // (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
            // (*dataArrayP)[i].length = 15;
    
            // if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
            // else result = COAP_500_INTERNAL_SERVER_ERROR;
            break;
        // case RES_0_OWNERSHIP_PRIORITY: //heh cannot be read apparently
        //     (*dataArrayP)[i].value =  (char *)lwm2m_malloc(255);  
        //     strncpy((*dataArrayP)[i].value, (char*)data->OwnershipPriority, 255);           
        //     (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
        //     (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
        //     (*dataArrayP)[i].length = 255;
    
        //     if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
        //     else result = COAP_500_INTERNAL_SERVER_ERROR;
        //     break;
        // case RES_0_LIGHT_BEHAVIOR: //heh cannot be read apparently
        //     (*dataArrayP)[i].value =  (char *)lwm2m_malloc(255);  
        //     strncpy((*dataArrayP)[i].value, (char*)data->LightBehavior, 255);           
        //     (*dataArrayP)[i].type = LWM2M_TYPE_RESOURCE;
        //     (*dataArrayP)[i].dataType = LWM2M_TYPE_STRING;
        //     (*dataArrayP)[i].length = 255;
    
        //     if ((*dataArrayP)[i].length != 0) result = COAP_205_CONTENT;
        //     else result = COAP_500_INTERNAL_SERVER_ERROR;
        //     break;
        default:
            result = COAP_404_NOT_FOUND;
        }
        i++;
    } while (i < *numDataP && result == COAP_205_CONTENT);

    return result;
}

// static uint8_t prv_device_discover(uint16_t instanceId,
//                                    int * numDataP,
//                                    lwm2m_data_t ** dataArrayP,
//                                    lwm2m_object_t * objectP)
// {
//     uint8_t result;
//     int i;

//     // this is a single instance object
//     if (instanceId != 0)
//     {
//         return COAP_404_NOT_FOUND;
//     }

//     result = COAP_205_CONTENT;

//     // is the server asking for the full object ?
//     if (*numDataP == 0)
//     {
//         uint16_t resList[] = {
//             RES_O_MANUFACTURER,
//             RES_O_MODEL_NUMBER,
//             RES_O_SERIAL_NUMBER,
//             RES_O_FIRMWARE_VERSION,
//             RES_M_REBOOT,
//             RES_O_FACTORY_RESET,
//             RES_O_AVL_POWER_SOURCES,
//             RES_O_POWER_SOURCE_VOLTAGE,
//             RES_O_POWER_SOURCE_CURRENT,
//             RES_O_BATTERY_LEVEL,
//             RES_O_MEMORY_FREE,
//             RES_M_ERROR_CODE,
//             RES_O_RESET_ERROR_CODE,
//             RES_O_CURRENT_TIME,
//             RES_O_UTC_OFFSET,
//             RES_O_TIMEZONE,
//             RES_M_BINDING_MODES
//         };
//         int nbRes = sizeof(resList) / sizeof(uint16_t);

//         *dataArrayP = lwm2m_data_new(nbRes);
//         if (*dataArrayP == NULL) return COAP_500_INTERNAL_SERVER_ERROR;
//         *numDataP = nbRes;
//         for (i = 0; i < nbRes; i++)
//         {
//             (*dataArrayP)[i].id = resList[i];
//         }
//     }
//     else
//     {
//         for (i = 0; i < *numDataP && result == COAP_205_CONTENT; i++)
//         {
//             switch ((*dataArrayP)[i].id)
//             {
//             case RES_O_MANUFACTURER:
//             case RES_O_MODEL_NUMBER:
//             case RES_O_SERIAL_NUMBER:
//             case RES_O_FIRMWARE_VERSION:
//             case RES_M_REBOOT:
//             case RES_O_FACTORY_RESET:
//             case RES_O_AVL_POWER_SOURCES:
//             case RES_O_POWER_SOURCE_VOLTAGE:
//             case RES_O_POWER_SOURCE_CURRENT:
//             case RES_O_BATTERY_LEVEL:
//             case RES_O_MEMORY_FREE:
//             case RES_M_ERROR_CODE:
//             case RES_O_RESET_ERROR_CODE:
//             case RES_O_CURRENT_TIME:
//             case RES_O_UTC_OFFSET:
//             case RES_O_TIMEZONE:
//             case RES_M_BINDING_MODES:
//                 break;
//             default:
//                 result = COAP_404_NOT_FOUND;
//             }
//         }
//     }

//     return result;
// }

static uint8_t prv_light_device_write(uint16_t instanceId,
                                int numData,
                                lwm2m_data_t * dataArray,
                                lwm2m_object_t * objectP)
{
    int i;
    uint8_t result;

    uint8_t temp_int;
    float   temp_float;
    light_device_data_t * data = (light_device_data_t*)(objectP->userData);

    // this is a single instance object
    if (instanceId != 0)
    {
        return COAP_404_NOT_FOUND;
    }

    i = 0;

    do
    {
        switch (dataArray[i].id)
        {
        case RES_0_LIGHT_STATE:
            strncpy((char*) &(data->LightState), "\0", 5);
            // strncpy((char*) &(data->LightState), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            strncpy((char*) &(data->LightState), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        case RES_0_USER_TYPE:
            strncpy((char*) &(data->UserType), "\0", 10);
            strncpy((char*) &(data->UserType), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        case RES_0_USER_ID:
            strncpy((char*) &(data->UserID), "\0", 20);
            strncpy((char*) &(data->UserID), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        case RES_0_LIGHT_COLOR:
            strncpy((char*) &(data->LightColor), "\0", 20);
            strncpy((char*) &(data->LightColor), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        case RES_0_LOW_LIGHT:
            if (1 == lwm2m_data_decode_int(dataArray + i, &(temp_int)))
            {
                data->LowLight = temp_int;
                result = COAP_204_CHANGED;
            }
            else
                result = COAP_400_BAD_REQUEST;

            break;
        case RES_0_GROUP_NO:
            if (1 == lwm2m_data_decode_int(dataArray + i, &(temp_int)))
            {
                data->GroupNo = temp_int;
                result = COAP_204_CHANGED;
            }
            else
                result = COAP_400_BAD_REQUEST;

            break;
        case RES_0_LOCATION_X:
            if (1 == lwm2m_data_decode_float(dataArray + i, &(temp_float)))
            {
                data->LocationX = temp_float;
                result = COAP_204_CHANGED;
            }
            else
                result = COAP_400_BAD_REQUEST;

            break;
        case RES_0_LOCATION_Y:
            if (1 == lwm2m_data_decode_float(dataArray + i, &(temp_float)))
            {
                data->LocationY = temp_float;
                result = COAP_204_CHANGED;
            }
            else
                result = COAP_400_BAD_REQUEST;

            break;
        case RES_0_ROOM_ID:
            strncpy((char*) &(data->RoomID), "\0", 10);
            strncpy((char*) &(data->RoomID), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        case RES_0_BEHAVIOR_DEPLOYMENT:
            strncpy((char*) &(data->BehaviorDeployment), "\0", 15);
            strncpy((char*) &(data->BehaviorDeployment), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        case RES_0_OWNERSHIP_PRIORITY:
            strncpy((char*) &(data->OwnershipPriority), "\0", 255);
            strncpy((char*) &(data->OwnershipPriority), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        case RES_0_LIGHT_BEHAVIOR:
            strncpy((char*) &(data->LightBehavior), "\0", 255);
            strncpy((char*) &(data->LightBehavior), (char*)dataArray[i].value.asBuffer.buffer, dataArray[i].value.asBuffer.length);
            result = COAP_204_CHANGED;

            break;
        default:
            result = COAP_405_METHOD_NOT_ALLOWED;
        }

        i++;
    } while (i < numData && result == COAP_204_CHANGED);

    return result;
}

// static uint8_t prv_device_execute(uint16_t instanceId,
//                                   uint16_t resourceId,
//                                   uint8_t * buffer,
//                                   int length,
//                                   lwm2m_object_t * objectP)
// {
//     // this is a single instance object
//     if (instanceId != 0)
//     {
//         return COAP_404_NOT_FOUND;
//     }

//     if (length != 0) return COAP_400_BAD_REQUEST;

//     switch (resourceId)
//     {
//     case RES_M_REBOOT:
//         fprintf(stdout, "\n\t REBOOT\r\n\n");
//         g_reboot = 1;
//         return COAP_204_CHANGED;
//     case RES_O_FACTORY_RESET:
//         fprintf(stdout, "\n\t FACTORY RESET\r\n\n");
//         return COAP_204_CHANGED;
//     case RES_O_RESET_ERROR_CODE:
//         fprintf(stdout, "\n\t RESET ERROR CODE\r\n\n");
//         ((light_device_data_t*)(objectP->userData))->error = 0;
//         return COAP_204_CHANGED;
//     default:
//         return COAP_405_METHOD_NOT_ALLOWED;
//     }
// }

// void display_light_device_object(lwm2m_object_t * object)
// {
// #ifdef WITH_LOGS
//     light_device_data_t * data = (light_device_data_t *)object->userData;
//     fprintf(stdout, "  /%u: Device object:\r\n", object->objID);
//     if (NULL != data)
//     {
//         fprintf(stdout, "    time: %lld, time_offset: %s\r\n",
//                 (long long) data->time, data->time_offset);
//     }
// #endif
// }

lwm2m_object_t* get_light_object_device(void)
{
    /*
     * The get_object_device function create the object itself and return a pointer to the structure that represent it.
     */
    lwm2m_object_t* deviceObj;

    deviceObj = (lwm2m_object_t *)lwm2m_malloc(sizeof(lwm2m_object_t));

    if (NULL != deviceObj)
    {
        memset(deviceObj, 0, sizeof(lwm2m_object_t));

        /*
         * It assigns his unique ID
         * The 3 is the standard ID for the mandatory object "Object device".
         */
        deviceObj->objID = LWM2M_LIGHT_DEVICE_OBJECT_ID;

        /*
         * and its unique instance
         *
         */
        deviceObj->instanceList = (lwm2m_list_t *)lwm2m_malloc(sizeof(lwm2m_list_t));
        if (NULL != deviceObj->instanceList)
        {
            memset(deviceObj->instanceList, 0, sizeof(lwm2m_list_t));
        }
        else
        {
            lwm2m_free(deviceObj);
            return NULL;
        }
        
        /*
         * And the private function that will access the object.
         * Those function will be called when a read/write/execute query is made by the server. In fact the library don't need to
         * know the resources of the object, only the server does.
         */
        deviceObj->readFunc     = prv_light_device_read;
        // deviceObj->discoverFunc = prv_device_discover;
        deviceObj->writeFunc    = prv_light_device_write;
        // deviceObj->executeFunc  = prv_device_execute;
        deviceObj->userData = lwm2m_malloc(sizeof(light_device_data_t));

        /*
         * Also some user data can be stored in the object with a private structure containing the needed variables 
         */
        if (NULL != deviceObj->userData)
        {
            light_device_data_t* data = (light_device_data_t*)deviceObj->userData;
            strcpy(data->LightID, "Light-Device-31-1");
            strcpy(data->DeviceType, "Light Device");
            strcpy(data->LightState, "FREE");
            strcpy(data->BehaviorDeployment, "Distributed");
            data->GroupNo = 31;
            // ((light_device_data_t*)deviceObj->userData)->battery_level = PRV_BATTERY_LEVEL;
            // ((light_device_data_t*)deviceObj->userData)->free_memory   = PRV_MEMORY_FREE;
            // ((light_device_data_t*)deviceObj->userData)->error = PRV_ERROR_CODE;
            // ((light_device_data_t*)deviceObj->userData)->time  = 1367491215;
            // strcpy(((light_device_data_t*)deviceObj->userData)->time_offset, "+01:00");
        }
        else
        {
            lwm2m_free(deviceObj->instanceList);
            lwm2m_free(deviceObj);
            deviceObj = NULL;
        }
    }

    return deviceObj;
}

void free_light_object_device(lwm2m_object_t * objectP)
{
    if (NULL != objectP->userData)
    {
        lwm2m_free(objectP->userData);
        objectP->userData = NULL;
    }
    if (NULL != objectP->instanceList)
    {
        lwm2m_free(objectP->instanceList);
        objectP->instanceList = NULL;
    }

    lwm2m_free(objectP);
}

// uint8_t device_change(lwm2m_data_t * dataArray,
//                       lwm2m_object_t * objectP)
// {
//     uint8_t result;

//     switch (dataArray->id)
//     {
//     case RES_O_BATTERY_LEVEL:
//             {
//                 int64_t value;
//                 if (1 == lwm2m_data_decode_int(dataArray, &value))
//                 {
//                     if ((0 <= value) && (100 >= value))
//                     {
//                         ((light_device_data_t*)(objectP->userData))->battery_level = value;
//                         result = COAP_204_CHANGED;
//                     }
//                     else
//                     {
//                         result = COAP_400_BAD_REQUEST;
//                     }
//                 }
//                 else
//                 {
//                     result = COAP_400_BAD_REQUEST;
//                 }
//             }
//             break;
//         case RES_M_ERROR_CODE:
//             if (1 == lwm2m_data_decode_int(dataArray, &((light_device_data_t*)(objectP->userData))->error))
//             {
//                 result = COAP_204_CHANGED;
//             }
//             else
//             {
//                 result = COAP_400_BAD_REQUEST;
//             }
//             break;
//         case RES_O_MEMORY_FREE:
//             if (1 == lwm2m_data_decode_int(dataArray, &((light_device_data_t*)(objectP->userData))->free_memory))
//             {
//                 result = COAP_204_CHANGED;
//             }
//             else
//             {
//                 result = COAP_400_BAD_REQUEST;
//             }
//             break;
//         default:
//             result = COAP_405_METHOD_NOT_ALLOWED;
//             break;
//         }
    
//     return result;
// }
