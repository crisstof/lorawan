
DATA_TYPE_NAME = "LevelM"
DATA_TYPE_ID   = 0x20


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    level   = payload[0] | (payload[1] << 8)
    payload = payload[2:]
    
    res['level']      = round(level / 1000.0, 3)
    res['level-unit'] = 'm'
    
    return payload
