#!/bin/sh

date1=$(date +'%Y%m%d')
mosquitto_sub -v -t "+/+/+/+/+" > /home/loraserver/testmosq/testmosq$date1.json

