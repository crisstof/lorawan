DATA_TYPE_NAME = "HeaterStatus"
DATA_TYPE_ID   = 0x1b


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    b       =  payload[0]
    is_on   = (b & 0x01 != 0)
    payload =  payload[1:]
    
    res['heater-isOn'] = is_on
    
    return payload
