

DATA_TYPE_NAME = "IlluminanceLux"
DATA_TYPE_ID   = 0x08


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0] | (payload[1] << 8)
    payload = payload[2:]
    
    res['illuminance']      = value
    res['illuminance-unit'] = 'lux'
    
    return payload
