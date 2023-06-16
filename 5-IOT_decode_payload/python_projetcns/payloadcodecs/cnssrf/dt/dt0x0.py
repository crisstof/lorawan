from datetime import datetime, timedelta


DATA_TYPE_NAME = "TimestampUTC"
DATA_TYPE_ID   = 0x00
tsref          = datetime(2000, 1, 1)


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    ts2000  = payload[0] | (payload[1] << 8) | (payload[2] << 16) | (payload[3] << 24)
    payload = payload[4:]
    ts      = tsref + timedelta(seconds = ts2000)
    ts_str  = ts.strftime("%Y-%m-%dT%H:%M:%S")

    if channel is 0:
        frame_global_values["node-timestampUTC"] = ts_str
    else:
        res["timestampUTC"] = ts_str
    
    return payload
