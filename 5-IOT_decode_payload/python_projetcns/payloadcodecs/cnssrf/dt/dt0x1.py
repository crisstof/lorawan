DATA_TYPE_NAME = "BattVoltageMV"
DATA_TYPE_ID   = 0x01


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = payload[0] | (payload[1] << 8)
    payload = payload[2:]
    
    if channel is 0:
        frame_global_values['node-battery-voltage']      = round(value / 1000.0, 3)
        frame_global_values['node-battery-voltage-unit'] = 'V'
    else:
        res['battery-voltage']      = round(value / 1000.0, 3)
        res['battery-voltage-unit'] = 'V'
    
    return payload
