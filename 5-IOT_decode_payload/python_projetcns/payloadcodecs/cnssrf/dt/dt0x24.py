# -*- coding: utf-8 -*-


DATA_TYPE_NAME = "ConfigMM3Hash32"
DATA_TYPE_ID   = 0x24


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    h       = payload[0] | (payload[1] << 8) | (payload[2] << 16) | (payload[3] << 24)
    payload = payload[4:]

    frame_global_values["CNSSRFConfigMM3Hash32"] = format(h, '08X')
    
    return payload
