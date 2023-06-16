# -*- coding: utf-8 -*-


DATA_TYPE_NAME = "SensorTypeMM3Hash32"
DATA_TYPE_ID   = 0x23


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    h       = payload[0] | (payload[1] << 8) | (payload[2] << 16) | (payload[3] << 24)
    payload = payload[4:]

    channel_global_values["CNSSRFSensorTypeMM3Hash32"] = format(h, '08X')
    
    return payload
