
DATA_TYPE_NAME = "SolutionConductivitySCm"
DATA_TYPE_ID   = 0x0a


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0] | (payload[1] << 8) | (payload[2] << 16)
    payload = payload[3:]
    
    value                            = round(value * 0.05, 2)
    res['solutionConductivity']      = value
    res['solutionConductivity-unit'] = u'S.cm\u207b\u00b9'
    
    return payload
