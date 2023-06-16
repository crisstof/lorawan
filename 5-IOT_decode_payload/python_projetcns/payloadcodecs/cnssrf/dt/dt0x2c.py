DATA_TYPE_NAME = "ResetSource"
DATA_TYPE_ID   = 0x2c


RESET_ID_TO_NAME = {
    0x1: "BOR",
    0x2: "resetPin",
    0x3: "software",
    0x4: "softwareError",
    0x5: "watchdog",
    0x6: "independentWatchdog",
    0x7: "lowPowerError",
    0x8: "optionBytesLoading",
    0x9: "firewall"
}


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    resetId = payload[0] & 0x0F
    payload = payload[1:]
    
    name = RESET_ID_TO_NAME.get(resetId, "")
    
    res["resetSource-id"]   = resetId
    res["resetSource-name"] = name
    
    return payload
