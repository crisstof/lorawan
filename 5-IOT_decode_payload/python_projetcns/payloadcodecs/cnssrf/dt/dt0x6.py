
DATA_TYPE_NAME = "GeographicalPosition3D"
DATA_TYPE_ID   = 0x06


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    latitude  = payload[0] | (payload[1] << 8) | (payload[2] << 16)
    longitude = payload[3] | (payload[4] << 8) | (payload[5] << 16)
    altitude  = payload[6] | (payload[7] << 8) | (payload[8] << 16)
    payload   = payload[9:]
    
    latitude  = round(latitude  * 0.000025 - 180.0,  6)
    longitude = round(longitude * 0.000025 - 180.0,  6)
    altitude  = round(altitude  * 0.01     - 7000.0, 2)
    
    if channel == 0:
        frame_global_values['node-geoPos-latitude']       = latitude
        frame_global_values['node-geoPos-latitude-unit']  = '°'
        frame_global_values['node-geoPos-longitude']      = longitude
        frame_global_values['node-geoPos-longitude-unit'] = '°'
        frame_global_values['node-geoPos-altitude']       = altitude
        frame_global_values['node-geoPos-altitude-unit']  = 'm'
    else:
        res['geoPos-latitude']       = latitude
        res['geoPos-latitude-unit']  = '°'
        res['geoPos-longitude']      = longitude
        res['geoPos-longitude-unit'] = '°'
        res['geoPos-altitude']       = altitude
        res['geoPos-altitude-unit']  = 'm'
    
    return payload
