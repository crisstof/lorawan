DATA_TYPE_NAME = "TempDegC1"
DATA_TYPE_ID   = 0x02

VALUE_OFFSET = -273.2


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   =  payload[0] | ((payload[1] & 0x3F) << 8)
    alarm_l = (payload[1] & 0x40) != 0
    alarm_h = (payload[1] & 0x80) != 0
    payload =  payload[2:]
    
    value                     = (value / 10.0) + VALUE_OFFSET
    value                     = round(value, 1) 
    res['temperature']        = value
    res['temperature-unit']   = '°C'
    res['temperature-alarmH'] = alarm_h
    res['temperature-alarmL'] = alarm_l
    
    return payload
