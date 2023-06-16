DATA_TYPE_NAME = "AppSoftwareVersionMMPHash32"
DATA_TYPE_ID   = 0x2b


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    v       =   payload[0] | (payload[1] << 8)
    hash32  =   payload[2] | (payload[3] << 8) | (payload[4] << 16) | (payload[5] << 24)
    payload = payload[6:]
    
    major =  (v & 0x7C00) >> 10
    minor =  (v & 0x03F0) >> 4
    patch =   v & 0x000F
    isDev = ((v & 0x8000) != 0)
    
    version = "{0}.{1}.{2}".format(major, minor, patch)
    if isDev:
        version = version + "-dev"
    version = version + " (r{0:8x})".format(hash32)

    if channel is 0:
        frame_global_values["node-appVersion"] = version
    else:
        res["appVersion"] = version
    
    return payload
