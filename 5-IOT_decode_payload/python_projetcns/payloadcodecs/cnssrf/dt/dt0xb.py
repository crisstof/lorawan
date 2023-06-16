
DATA_TYPE_NAME = "DigitalInput"
DATA_TYPE_ID   = 0x0b


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0]
    payload = payload[1:]
    
    res['input-type']  = 'digitalInput'
    res['input-id']    = value >> 1
    res['input-level'] = value & 0x01
    res['input-unit']  = 'high/low'
    
    return payload
