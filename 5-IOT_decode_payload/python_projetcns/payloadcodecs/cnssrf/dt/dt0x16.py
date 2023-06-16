

DATA_TYPE_NAME = "WindSpeedDirection"
DATA_TYPE_ID   = 0x16


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    direction          =   payload[0]               | ((payload[1] & 0x01) << 8)
    speed              = ((payload[1] & 0xFE) >> 1) | ((payload[2] & 0x3F) << 7)
    dir_is_corrected   =  (payload[2] & 0x40) != 0
    speed_is_corrected =  (payload[2] & 0x80) != 0
    payload            =   payload[3:]
    
    res['windSpeed']                 = round(speed * 0.01, 2)
    res['windSpeed-unit']            = u'm.s\u207b\u00b9'
    res['windSpeed-isCorrected']     = speed_is_corrected
    res['windDirection']             = direction
    res['windDirection-unit']        = u'°'
    res['windDirection-isCorrected'] = dir_is_corrected
    
    return payload

