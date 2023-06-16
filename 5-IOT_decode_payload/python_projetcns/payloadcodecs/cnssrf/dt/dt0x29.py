
DATA_TYPE_NAME = "WindGustSpeedMS"
DATA_TYPE_ID   = 0x29


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    speed        =   payload[0] | ((payload[1] & 0x1F) << 8)
    is_corrected =  (payload[1] & 0x20) != 0
    period_sec   =   payload[2]               | ((payload[3] & 0x0F) << 8)
    step_sec     = ((payload[3] & 0xF0) >> 4) |  (payload[4] << 8) 
    payload      =   payload[5:]
    
    res['windGust-speed']               = round(speed * 0.01, 2)
    res['windGust-speed-unit']          = u'm.s\u207b\u00b9'
    res['windGust-speed-isCorrected']   = is_corrected
    res['windGust-avgPeriod']           = period_sec
    res['windGust-avgPeriod-unit']      = 's'
    res['windGust-avgRollingStep']      = step_sec
    res['windGust-avgRollingStep-unit'] = 's'
    res['windGust-avgUseRolling']       = (step_sec != 0)
    
    return payload

