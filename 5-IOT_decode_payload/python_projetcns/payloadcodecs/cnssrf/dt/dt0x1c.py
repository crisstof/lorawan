
DATA_TYPE_NAME = "DepthCm"
DATA_TYPE_ID   = 0x1c


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    depth = payload[0] & 0x7F
    if (payload[0] & 0x80) != 0:
        depth   = depth | (payload[1] << 7)
        payload = payload[2:]
    else:
        payload = payload[1:]
    
    res['depth']      = depth
    res['depth-unit'] = 'cm'
    
    return payload
