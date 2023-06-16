
DATA_TYPE_NAME = "SolarIrradianceWM2"
DATA_TYPE_ID   = 0x19


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    irradiance = payload[0] | ((payload[1] & 0x3F) << 8)
    payload    = payload[2:]
    
    res['solarIrradiance']      = round(speed * 0.1, 1)
    res['solarIrradinace-unit'] = 'W/m²'
    
    return payload

