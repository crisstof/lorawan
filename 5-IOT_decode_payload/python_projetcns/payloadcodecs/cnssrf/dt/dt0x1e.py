
DATA_TYPE_NAME = "SoilVolumetricWaterContentPercent"
DATA_TYPE_ID   = 0x1e


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0] | (payload[1] & 0x3F) << 8
    payload = payload[2:]
    
    res['soilVolumetricWaterContent']      = round(value / 100.0, 2)
    res['soilVolumetricWaterContent-unit'] = '%'
    
    return payload
