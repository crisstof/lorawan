

DATA_TYPE_NAME = "SoilMoistureCb"
DATA_TYPE_ID   = 0x10


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    i     = 0
    count = 0;
    
    while True:
        depthCm  = payload[i] & 0x3F
        alarmLow = alarmHigh = False
        more     = (payload[i] & 0x80) != 0
        
        if (payload[i] & 0x40) != 0:
            # Long format
            i         = i + 1
            depthCm   = depthCm | (payload[i] & 0x07) << 6
            alarmLow  = ((payload[i] & 0x40) != 0)
            alarmHigh = ((payload[i] & 0x80) != 0)
            i         = i + 1
            value     = payload[i]
        else:
            #Short format
            i         = i + 1
            value     = payload[i]   
        i = i + 1  
    
        count  = count + 1
        prefix = "depth{0}-".format(count)
        res[prefix + 'depth']                      = depthCm
        res[prefix + 'depth-unit']                 = 'cm'
        res[prefix + 'soilWaterTension']           = value
        res[prefix + 'soilWaterTension-unit']      = 'cb'
        res[prefix + 'soilWaterTension-alarmLow']  = alarmLow
        res[prefix + 'soilWaterTension-alarmHigh'] = alarmHigh
        if not more: break 
    
    return payload[i:]
