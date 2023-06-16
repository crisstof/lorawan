
from struct import Struct

DATA_TYPE_NAME = "Acceleration3DG"
DATA_TYPE_ID   = 0x0d

depacker       = Struct('<hhh')


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    x, y, z = depacker.unpack(payload[0:6])
    payload = payload[6:]
    
    res['acceleration-axisX'] = round(x * 0.001, 3)
    res['acceleration-axisY'] = round(y * 0.001, 3)
    res['acceleration-axisZ'] = round(z * 0.001, 3)
    res['acceleration-unit']  = 'G'
    
    return payload
