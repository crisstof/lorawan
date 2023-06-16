from struct import Struct

DATA_TYPE_NAME = "ConcentrationUgL"
DATA_TYPE_ID   = 0x34

STRUCT         = Struct('<f')

def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    print("Payload len: {0}".format(len(payload)))
    value   = STRUCT.unpack(payload[0:4])[0]
    payload = payload[4:]
    
    res['concentration'] = round(value, 2)
    res['concentration-unit'] = "UgL"
    
    return payload
