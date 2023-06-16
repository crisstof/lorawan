'

DATA_TYPE_NAME = "WindSpeedMS"
DATA_TYPE_ID   = 0x17


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    speed        =  payload[0] | ((payload[1] & 0x1F) << 8)
    is_corrected = (payload[1] & 0x20) != 0
    payload      =  payload[2:]
    
    res['windSpeed']             = round(speed * 0.01, 2)
    res['windSpeed-unit']        = u'm.s\u207b\u00b9'
    res['windSpeed-isCorrected'] = is_corrected
    
    return payload

