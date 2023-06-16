

DATA_TYPE_NAME = "GeographicalPosition2D"
DATA_TYPE_ID   = 0x07


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    latitude  = payload[0] | (payload[1] << 8) | (payload[2] << 16)
    longitude = payload[3] | (payload[4] << 8) | (payload[5] << 16)
    payload   = payload[6:]
    
    latitude  = round(latitude  * 0.000025 - 180.0, 6)
    longitude = round(longitude * 0.000025 - 180.0, 6)
    
    if channel == 0:
        frame_global_values['node-geoPos-latitude']       = latitude
        frame_global_values['node-geoPos-latitude-unit']  = '°'
        frame_global_values['node-geoPos-longitude']      = longitude
        frame_global_values['node-geoPos-longitude-unit'] = '°'
    else:
        res['geoPos-latitude']       = latitude
        res['geoPos-latitude-unit']  = '°'
        res['geoPos-longitude']      = longitude
        res['geoPos-longitude-unit'] = '°'
    
    return payload
