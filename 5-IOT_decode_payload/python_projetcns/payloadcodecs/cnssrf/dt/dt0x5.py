
DATA_TYPE_NAME = "AirHumidityRelPercent"
DATA_TYPE_ID   = 0x05


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0]
    payload = payload[1:]
    
    value                   = value / 2.0 
    res['airHumidity']      = value
    res['airHumidity-unit'] = '%'
    
    return payload
