from struct import Struct

DATA_TYPE_NAME = "RelativeDielectricPermittivity"
DATA_TYPE_ID   = 0x1d

STRUCT         = Struct('<f')


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    print("Payload len: {0}".format(len(payload)))
    value   = STRUCT.unpack(payload[0:4])[0]
    payload = payload[4:]
    
    res['relativeDielectricPermittivity'] = round(value, 2)
    
    return payload
