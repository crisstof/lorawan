

DATA_TYPE_NAME = "IlluminanceLuxHiRes"
DATA_TYPE_ID   = 0x09


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0] | (payload[1] << 8) | (payload[2] << 16) | (payload[3] << 24)
    payload = payload[4:]
    
    res['illuminance']      = round(value * 0.0001, 4)
    res['illuminance-unit'] = 'lux'
    
    return payload
