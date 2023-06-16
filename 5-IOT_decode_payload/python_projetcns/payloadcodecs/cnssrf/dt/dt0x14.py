DATA_TYPE_NAME = "PressurePa"
DATA_TYPE_ID   = 0x14


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value    =  payload[0] | (payload[1] << 8) | (payload[2] << 16) | ((payload[3] & 0x0F) << 24)
    absolute = (payload[2] & 0x20) != 0
    alarm_l  = (payload[2] & 0x40) != 0
    alarm_h  = (payload[2] & 0x80) != 0
    if (payload[2] & 0x10) != 0:
        sign = -1.0
    else:
        sign =  1.0
    payload  =  payload[4:]
    
    res['pressure']          = round(sign * value * 0.1, 1)
    res['pressure-unit']     = 'Pa'
    res['pressure-absolute'] = absolute
    res['pressure-alarmH']   = alarm_h
    res['pressure-alarmL']   = alarm_l
    
    return payload
