#!/bin/sh

date1=$(date +'%Y%m%d')
mosquitto_sub -v -t "application/+/node/+/rx" > /home/loraserver/rawdata/rawdata$date1.json
