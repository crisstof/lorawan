
DATA_TYPE_NAME = "Config"
DATA_TYPE_ID   = 0x15


class ParamInfos:
    def __init__(self, name, value_process_fn):
        self._name             = name
        self._value_process_fn = value_process_fn
        
        
    def name(self):
        return self._name
        

    def process_value(self, value):
        if self._value_process_fn:
            return self._value_process_fn(value)
        return value


def str_to_uint32(s):
    return int(s)


param_id_infos = { 
0x01: ParamInfos("name",                   None),
0x02: ParamInfos("uniqueId",               None),
0x03: ParamInfos("type",                   None),
0x04: ParamInfos("firmwareVersion",        None),
0x05: ParamInfos("experimentName",         None),
0x06: ParamInfos("sensorReadingPeriodSec", str_to_uint32),
0x07: ParamInfos("sendConfigPeriodSec",    str_to_uint32),
0x08: ParamInfos("GPSReadingPeriodSec",    str_to_uint32)
}


def decode_payload(payload, 
                   channel, 
                   res, 
                   frame_global_values, 
                   channel_global_values):
    param_id        = payload[0] & 0x3F
    param_value_len = payload[1] & 0x1F
    param_value     = payload[2:2 + param_value_len]
    payload         = payload[2   + param_value_len :]
    
    param_name = 'unknown'
    infos      = None
    try:
        infos      = param_id_infos[param_id]
        param_name = infos.name()
    except KeyError:
        pass
        
    # Decode string value
    value = None
    try:
        value = param_value.decode('utf-8')
    except UnicodeDecodeError:
        pass
    if not value:
        try:
            value = param_value.decode('cp1252')
        except UnicodeDecodeError:
            pass
    if not value:
        try:
            value = param_value.decode('latin-1')
        except UnicodeDecodeError:
            pass
    if not value:
        try:
            value = param_value.decode('iso8859-15')
        except UnicodeDecodeError:
            pass
            
    if infos:
        value = infos.process_value(value)

    res['configParameter'] = param_name
    res['configValue']     = value
    
    return payload
