DATA_TYPE_NAME = "SolutionConductivityUSCm"
DATA_TYPE_ID   = 0x12


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   =  payload[0] | (payload[1] << 8) | ((payload[2] & 0x3F) << 16)
    alarm_l = (payload[2] & 0x40) != 0
    alarm_h = (payload[2] & 0x80) != 0
    payload =  payload[3:]
    
    res['solutionConductivity']        = round(value / 10, 1)
    res['solutionConductivity-unit']   = u'µS.cm\u207b\u00b9'
    res['solutionConductivity-alarmH'] = alarm_h
    res['solutionConductivity-alarmL'] = alarm_l
    
    return payload
