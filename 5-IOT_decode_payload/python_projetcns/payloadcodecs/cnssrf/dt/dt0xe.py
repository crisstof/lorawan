
DATA_TYPE_NAME = "RainAmountMM"
DATA_TYPE_ID   = 0x0e


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    timeSec = payload[0] | (payload[1] << 8) | (payload[2] << 16)
    value   = payload[3] | (payload[4] << 8);
    payload = payload[5:]
    
    res['rainAmount']           = round((value & 0x3FFF) * 0.1, 1)
    res['rainAmount-unit']      = 'mm'
    res['rainAmount-time']      = timeSec
    res['rainAmount-time-unit'] = "s"
    res['rainAmount-alarm']     = ((value & 0x4000) != 0)
    
    return payload
