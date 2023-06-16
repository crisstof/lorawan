
DATA_TYPE_NAME = "WindAvgSpeedDirection"
DATA_TYPE_ID   = 0x25


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
    
    res['windAvg-speed']                 = round(speed * 0.01, 2)
    res['windAvg-speed-unit']            = u'm.s\u207b\u00b9'
    res['windAvg-speed-isCorrected']     = speed_is_corrected
    res['windAvg-direction']             = direction
    res['windAvg-direction-unit']        = u'°'
    res['windAvg-direction-isCorrected'] = dir_is_corrected
    res['windAvg-avgPeriod']             = period_sec
    res['windAvg-avgPeriod-unit']        = 's'
    res['windAvg-avgRollingStep']        = step_sec
    res['windAvg-avgRollingStep-unit']   = 's'
    res['windAvg-avgUseRolling']         = (step_sec != 0)
    
    return payload

