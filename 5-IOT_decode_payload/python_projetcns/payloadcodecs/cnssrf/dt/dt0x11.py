
DATA_TYPE_NAME = "SoilMoistureCbDegCHz"
DATA_TYPE_ID   = 0x11


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    i     = 0
    count = 0
    
    while True:
        # Get soil moisture base data
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
        
        # Get temperature
        tempDegC = -50 + (payload[i] / 2.0) 
        i        = i + 1
        
        # Get the frequency
        freqHz = 0
        j      = 0
        while True:            
            freqHz   = freqHz | (payload[i] & 0x7F) << j
            moreFreq = (payload[i] & 0x80) != 0
            i        = i + 1
            j        = j + 7
            if not moreFreq: break
    
        count  = count + 1
        prefix = "depth{0}-".format(count)
        res[prefix + 'depth']                      = depthCm
        res[prefix + 'depthUnit']                  = 'cm'
        res[prefix + 'soilWaterTension']           = value
        res[prefix + 'soilWaterTension-unit']      = 'cb'
        res[prefix + 'soilTemperature']            = tempDegC
        res[prefix + 'soilTemperature-unit']       = '°C'
        res[prefix + 'frequency']                  = freqHz
        res[prefix + 'frequency-unit']             = 'Hz'
        res[prefix + 'soilWaterTension-alarmLow']  = alarmLow
        res[prefix + 'soilWaterTension-alarmHigh'] = alarmHigh
        if not more: break 
    
    return payload[i:]
