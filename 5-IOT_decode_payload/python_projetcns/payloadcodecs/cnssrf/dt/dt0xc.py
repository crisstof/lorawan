
from struct import Struct

DATA_TYPE_NAME = "VoltageV"
DATA_TYPE_ID   = 0x0c

depacker       = Struct('<h')


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    value   = depacker.unpack(payload[0:2])
    payload = payload[2:]
    
    res['voltage']      = round(value * 0.01, 2)
    res['voltage-unit'] = 'V'
    
    return payload
