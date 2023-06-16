
DATA_TYPE_NAME = "WindAvgSpeedMS"
DATA_TYPE_ID   = 0x26


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
    
    res['windAvg-speed']               = round(speed * 0.01, 2)
    res['windAvg-speed-unit']          = u'm.s\u207b\u00b9'
    res['windAvg-speed-isCorrected']   = is_corrected
    res['windAvg-avgPeriod']           = period_sec
    res['windAvg-avgPeriod-unit']      = 's'
    res['windAvg-avgRollingStep']      = step_sec
    res['windAvg-avgRollingStep-unit'] = 's'
    res['windAvg-avgUseRolling']       = (step_sec != 0)
    
    return payload

