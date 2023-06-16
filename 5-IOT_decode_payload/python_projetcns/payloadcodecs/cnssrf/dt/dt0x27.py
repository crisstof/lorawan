
DATA_TYPE_NAME = "WindAvgDirectionDegN"
DATA_TYPE_ID   = 0x27


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    direction    =   payload[0] | ((payload[1] & 0x01) << 8)
    is_corrected =  (payload[1] & 0x02) != 0
    period_sec   =   payload[2]               | ((payload[3] & 0x0F) << 8)
    step_sec     = ((payload[3] & 0xF0) >> 4) |  (payload[4] << 8) 
    payload      =   payload52:]
    
    res['windAvg-direction']             = direction
    res['windAvg-direction-unit']        = u'°'
    res['windAvg-direction-isCorrected'] = is_corrected
    res['windAvg-avgPeriod']             = period_sec
    res['windAvg-avgPeriod-unit']        = 's'
    res['windAvg-avgRollingStep']        = step_sec
    res['windAvg-avgRollingStep-unit']   = 's'
    res['windAvg-avgUseRolling']         = (step_sec != 0)
    
    return payload

