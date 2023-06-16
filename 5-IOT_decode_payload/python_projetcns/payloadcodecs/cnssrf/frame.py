import importlib
import copy
import sys
import os.path
import inspect
import logging


logger   = logging.getLogger("CNSSRFFrame")
decoders = dict()


class DataTypeDecoder:
    def __init__(self, dt_id):
        self._id        = dt_id
        self._mod_name  = "payloadcodecs.cnssrf.dt.dt{0}".format(hex(dt_id))
        self._mod       = None
        self._mod_mtime = None
            
                        
    def decode_module(self):
        if self._mod:
            # We already have loaded the module
            # Does it's last modification date has changed since then?
            mtime = os.path.getmtime(inspect.getfile(self._mod))
            if mtime != self._mod_mtime:
                # Yes it has. Reload the module.
                try:
                    logger.info("CNSSRF Data Type decode module '{m}' has changed; reload it.".format(m = self._mod_name))
                    self._mod       = importlib.reload(self._mod)
                    self._mod_mtime = mtime
                except ModuleNotFoundError:
                    self._mod       = None
                    self._mod_mtime = None
                    logger.error("Failed to reload module '{m}': {e}.".format(m = self._mod_name, e = str(e)))
        else:
            # We haven't loaded the module yet. Do it now.
            try:
                logger.info("Import CNSSRF Data Type decode module '{m}'.".format(m = self._mod_name))
                self._mod       = importlib.import_module(self._mod_name)
                self._mod_mtime = os.path.getmtime(inspect.getfile(self._mod))
            except (ImportError, TypeError) as e:
                self._id        = None
                self._mod_name  = None
                logger.error("Failed to load module '{m}': {e}.".format(m = self._mod_name, e = str(e)))

        return self._mod
        
    


def decode_payload(payload):
    res                   = []
    global_values         = dict()
    channel_global_values = dict()
    
    # Get the format/version byte
    frame_version = payload[0] & 0x1F;
    frame_format  = payload[0] >> 5;
    if frame_format != 0x6:
        logger.error("Invalid frame format: {0}." .format(frame_format))
        return res
    if frame_version != 1:
        logger.error("Invalid frame version: {0}.".format(frame_version))
        return res
    payload = payload[1:]

    # Decode data channels
    while payload:
        payload = decode_data_channel(payload, res, global_values, channel_global_values)
    
    return res


def decode_data_channel(payload, 
                        res, 
                        frame_global_values,
                        channel_global_values):
    clear_global    = (payload[0] & 0x80) != 0
    data_channel_id = (payload[0] & 0x78) >> 3
    nb_data         =  payload[0] & 0x07
    payload         =  payload[1:]
    
    if clear_global:
        frame_global_values.clear()
        
    if frame_global_values.get('DataChannel', None) != data_channel_id:
        channel_global_values.clear()
    
    frame_global_values['DataChannel'] = data_channel_id
    
    data = dict()
    while nb_data:   
        nb_data = nb_data - 1
             
        # Decode Data Type id
        data_type_id = 0
        i            = 0
        while True:
            data_type_id = data_type_id | (payload[i] & 0x7F) << (i * 8)
            if payload[i] & 0x80 == 0:
                break;
            i = i + 1
        payload = payload[i + 1:]
            
        # Decode
        decoder = get_data_type_decoder(data_type_id).decode_module()
        if not decoder:
            raise Exception(
                "Cannot find decoder module for DataType 0x{xid}"
                .format(xid = hex(data_type_id)))
        payload = decoder.decode_payload(payload, 
                                         data_channel_id, 
                                         data, 
                                         frame_global_values,
                                         channel_global_values)
        
        # Write result
        if data or not payload:
            d_copy    = copy.deepcopy(frame_global_values)
            data_copy = copy.deepcopy(data)
            dcgv_copy = copy.deepcopy(channel_global_values)
            d_copy.update(dcgv_copy)
            d_copy.update(data_copy)
            d_copy['CNSSRFDataTypeId']   = data_type_id
            d_copy['CNSSRFDataTypeName'] = decoder.DATA_TYPE_NAME
            res.append(d_copy)
            data.clear()
    
    return payload


def get_data_type_decoder(data_type_id):
    # See if we already know the decoder for this data type
    # And if not create a new decoder object
    if not data_type_id in decoders:
        decoders[data_type_id] = DataTypeDecoder(data_type_id)
    
    # Return decoder module. Can be None.
    return decoders.get(data_type_id)
