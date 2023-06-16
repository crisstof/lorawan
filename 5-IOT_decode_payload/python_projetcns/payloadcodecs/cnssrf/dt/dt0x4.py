
DATA_TYPE_NAME = "PressAtmoHPa"
DATA_TYPE_ID   = 0x04


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0] | (payload[1] << 8)
    payload = payload[2:]
    
    value                           = round(700.0 + (value / 100.0), 2)
    res['atmosphericPressure']      = value
    res['atmosphericPressure-unit'] = 'hPa'
    
    return payload
