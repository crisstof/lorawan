
DATA_TYPE_NAME = "WindGustDirectionDegN"
DATA_TYPE_ID   = 0x2a


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    direction    =   payload[0] | ((payload[1] & 0x01) << 8)
    is_corrected =  (payload[1] & 0x02) != 0
    period_sec   =   payload[2]               | ((payload[3] & 0x0F) << 8)
    step_sec     = ((payload[3] & 0xF0) >> 4) |  (payload[4] << 8) 
    payload      =   payload[5:]
    
    res['windGust-direction']             = direction
    res['windGust-direction-unit']        = u'°'
    res['windGust-direction-isCorrected'] = is_corrected
    res['windGust-avgPeriod']             = period_sec
    res['windGust-avgPeriod-unit']        = 's'
    res['windGust-avgRollingStep']        = step_sec
    res['windGust-avgRollingStep-unit']   = 's'
    res['windGust-avgUseRolling']         = (step_sec != 0)
    
    return payload

