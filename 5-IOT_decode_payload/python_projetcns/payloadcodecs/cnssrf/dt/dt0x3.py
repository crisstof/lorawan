

DATA_TYPE_NAME = "TempDegCLowRes"
DATA_TYPE_ID   = 0x03


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0]
    payload = payload[1:]
    
    value                   = -50 + (value / 2.0) 
    res['temperature']      = value
    res['temperature-unit'] = '°C'
    
    return payload
