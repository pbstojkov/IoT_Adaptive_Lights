#!/bin/bash
while ! ifconfig | grep -F "192.168.43." > /dev/null; do
    sleep 1
    echo Zzz
done
#python2 light_main.py  > /dev/null
python2 sensor_main.py > /dev/null
