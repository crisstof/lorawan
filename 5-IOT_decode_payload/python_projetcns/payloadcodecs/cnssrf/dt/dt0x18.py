
DATA_TYPE_NAME = "WindDirectionDegN"
DATA_TYPE_ID   = 0x18


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    direction    =  payload[0] | ((payload[1] & 0x01) << 8)
    is_corrected = (payload[1] & 0x02) != 0
    payload      =  payload[2:]
    
    res['windDirection']             = direction
    res['windDirection-unit']        = u'°'
    res['windDirection-isCorrected'] = is_corrected
    
    return payload

