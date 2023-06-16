

from struct import Struct

DATA_TYPE_NAME = "VoltvvList"
DATA_TYPE_ID   = 0x32

depacker       = Struct('<iiiiiiiii')


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    t1, t2, t3, t4, t5, t6, t7, t8, tBatt = depacker.unpack(payload[0:36])
    payload = payload[36:]
    
    res['tension-ps1'] = round(t1 * 0.01, 2)
    res['tension-ps2'] = round(t2 * 0.01, 2)
    res['tension-ps3'] = round(t3 * 0.01, 2)
    res['tension-ps4'] = round(t4 * 0.01, 2)
    res['tension-ps5'] = round(t5 * 0.01, 2)
    res['tension-ps6'] = round(t6 * 0.01, 2)
    res['tension-ps7'] = round(t7 * 0.01, 2)
    res['tension-ps8'] = round(t8 * 0.01, 2)
    res['tension-Batt'] = round(tBatt * 0.01, 2)
    res['tension-unit']  = 'V'
   
    return payload
