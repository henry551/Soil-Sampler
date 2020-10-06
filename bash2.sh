#!/bin/bash

python3 Webcam2.py &
python3 webserver.py &
#watch -n1 scp values.txt pi@192.168.2.63:/home/pi/APP &

#echo "Running bash script"

while true; do
    if [ -e start.txt ]; then
        echo "START"
        break
    fi
done

rm start.txt
echo "START"
#sleep 10
#python3 parsedata.py
#sleep 2m
#ssh pi@192.168.2.63 'cd APP; python ALLSENSORS.py; exit'
echo "Connecting to Raspberry Pi"
ssh pi@192.168.2.63 'cd APP; echo "connected to Raspberry Pi"; python3 test2.py; exit'
#ssh pi@192.168.2.63 'cd APP; python3 ARM_MOVEMENT.py; python ALLSENSORS.py; exit'
#sftp pi@192.168.2.63:/home/pi/APP/sensor.txt
#cat sensor.txt
#python3 OutputValues6.py sensor.txt
