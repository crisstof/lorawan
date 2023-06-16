
DATA_TYPE_NAME = "TruebnerSMT100Raw"
DATA_TYPE_ID   = 0x1f


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0] | (payload[1] << 8)
    payload = payload[2:]
    
    res['raw'] = value
    
    return payload
