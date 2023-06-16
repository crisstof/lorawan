from struct import Struct

DATA_TYPE_NAME = "DeltaTempDegC"
DATA_TYPE_ID   = 0x31

STRUCT         = Struct('<h')


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = STRUCT.unpack(payload[0:2])[0]
    payload = payload[2:]
    
    res['deltaTemperature']      = round(value * 0.1, 1)
    res['deltaTemperature-unit'] = '°C'
    
    return payload

