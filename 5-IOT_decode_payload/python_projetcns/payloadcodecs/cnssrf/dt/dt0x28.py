
DATA_TYPE_NAME = "WindGustSpeedDirection"
DATA_TYPE_ID   = 0x28


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    direction          =   payload[0]               | ((payload[1] & 0x01) << 8)
    speed              = ((payload[1] & 0xFE) >> 1) | ((payload[2] & 0x3F) << 7)
    dir_is_corrected   =  (payload[2] & 0x40) != 0
    speed_is_corrected =  (payload[2] & 0x80) != 0
    period_sec         =   payload[3]               | ((payload[4] & 0x0F) << 8)
    step_sec           = ((payload[4] & 0xF0) >> 4) |  (payload[5] << 8) 
    payload            =   payload[6:]
    
    res['windGust-speed']                 = round(speed * 0.01, 2)
    res['windGust-speed-unit']            = u'm.s\u207b\u00b9'
    res['windGust-speed-isCorrected']     = speed_is_corrected
    res['windGust-direction']             = direction
    res['windGust-direction-unit']        = u'°'
    res['windGust-direction-isCorrected'] = dir_is_corrected
    res['windGust-avgPeriod']             = period_sec
    res['windGust-avgPeriod-unit']        = 's'
    res['windGust-avgRollingStep']        = step_sec
    res['windGust-avgRollingStep-unit']   = 's'
    res['windGust-avgUseRolling']         = (step_sec != 0)
    
    return payload

