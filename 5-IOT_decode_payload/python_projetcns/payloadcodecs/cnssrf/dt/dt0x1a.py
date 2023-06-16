DATA_TYPE_NAME = "RadioactivityBqM3"
DATA_TYPE_ID   = 0x1A


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value = 0
    i     = 0
    while True:
        b     = payload[i]
        more  = (b & 0x80) != 0
        value = value | ((b & 0x7F) << i * 7)
        i     = i + 1
        if not more: 
            payload = payload[i:]
            break
    
    res['radioactivity']      = value
    res['radioactivity-unit'] = u'Bq.m\u207b\u00b3'
    
    return payload
