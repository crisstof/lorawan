

DATA_TYPE_NAME = "BattVoltageFlagsMV"
DATA_TYPE_ID   = 0x0F


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value    = payload[0] | (payload[1] << 8)
    payload  = payload[2:]
    
    low_batt = (value & 0x1000) != 0 
    value    =  value & 0x0FFF
    
    if channel is 0:
        frame_global_values['node-batteryVoltage']            = round(value / 100.0, 2)
        frame_global_values['node-batteryVoltage-unit']       = 'V'
        frame_global_values['node-batteryVoltage-alarmIsLow'] = low_batt
    else:
        res['batteryVoltage']            = round(value / 100.0, 2)
        res['batteryVoltage-unit']       = 'V'
        res['batteryVoltage-alarmIsLow'] = low_batt
    
    return payload
