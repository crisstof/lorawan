import json
import base64
import datetime
import argparse
import sys
import os
import os.path
import inspect
import importlib


def update_path_to_get_module(module_name, required = True):
    libs_path  = None
    cmd_folder = os.path.dirname(inspect.getfile(inspect.currentframe()))
    if   os.path.isdir(os.path.join(cmd_folder, '..', module_name)):
        libs_path =    os.path.join(cmd_folder, '..')
    elif os.path.isdir(os.path.join(cmd_folder, '..', 'libs', 'python', module_name)):
        libs_path =    os.path.join(cmd_folder, '..', 'libs', 'python')
    elif os.path.isdir(os.path.join(cmd_folder, '..', 'libs', module_name)):
        libs_path =    os.path.join(cmd_folder, '..', 'libs')
    elif os.path.isdir(os.path.join(cmd_folder, '..', '..', 'libs', 'python', module_name)):
        libs_path =    os.path.join(cmd_folder, '..', '..', 'libs', 'python')
    elif os.path.isdir(os.path.join(cmd_folder, '..', '..', 'libs', module_name)):
        libs_path =    os.path.join(cmd_folder, '..', '..', 'libs')
    else:
        print("Failed to find path for module '{m}'.".format(m = module_name), file = sys.stderr)
        if required:
            sys.exit(1)
        return False
        
    if libs_path not in sys.path:
        sys.path.insert(0, libs_path)   
    return True
    
    
# Import our libraries
update_path_to_get_module('payloadcodecs')
update_path_to_get_module('mqttjsonflattener')
update_path_to_get_module('paho')
import mqttjsonflattener.mqttjsonflattener as flattener
import paho.mqtt.client                    as mqtt

# Do a first import of the CNSSRF frame decoder and keep its current last modification date
cnssrf_frame       = importlib.import_module('payloadcodecs.cnssrf.frame')
cnssrf_frame_mtime = os.path.getmtime(inspect.getfile(cnssrf_frame))

parser = argparse.ArgumentParser("Paho")
parser.add_argument('--data-no-list',     default = False, action = 'store_true', help = "The data field cannot contain a list; a single JSON line can produce several output JSON lines")
parser.add_argument('--data-flatten',     default = False, action = 'store_true', help = "Flatten the JSON data field")
parser.add_argument('-v', '--verbose',    default = False, action = 'store_true', help = "Print received message to stdout")
parser.add_argument('-o', '--output',     default = '', help = "Define output file")
parser.add_argument('-d', '--output-dir', default = '', help = "Output directory")
args = parser.parse_args()

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("application/+/node/+/rx")

def process_binary_message(jsonpayload, filename):
    print("TODO: REMOVE ME; for tests only. Process binary message.")
    try:
        print("TODO: REMOVE ME; #1.")
        data = base64.b64decode(jsonpayload['data'])
        print("TODO: REMOVE ME; #2.")
        
        # Check that the CNSSRF data frame decoder module has not changed
        if not cnssrf_frame:
            print("TODO: REMOVE ME; for tests only. CNSSRF module is None.")
        else:
            print("TODO: REMOVE ME; for tests only. CNSSRF module file: " + inspect.getfile(cnssrf_frame))
        mtime = os.path.getmtime(inspect.getfile(cnssrf_frame))
        print("TODO: REMOVE ME; #3.")
        if mtime != cnssrf_frame_mtime:
            # Module has changed. Reload it and update saved change time
            print("REMOVE ME; FOR TESTS ONLY: reload CNSSRF decode frame module.")
            cnssrf_frame       = importlib.reload(cnssrf_frame)
            cnssrf_frame_mtime = mtime
        
        # Decode CNSSRF data
        print("TODO: REMOVE ME; Decoding CNSSRF data...")
        jsonpayload['data'] = cnssrf_frame.decode_payload(data)
        print("TODO: REMOVE ME; Done.")
        jsonpayload['servertimestampUTC'] = datetime.datetime.utcnow().isoformat()
        lines = flattener.process_line(jsonpayload, args.data_no_list, args.data_flatten)
        print("TODO: REMOVE ME; After flattener.")
        with open(filename, 'a') as f:
            for l in lines:
                if l:
                    f.write(l + '\n')
                    if args.verbose:
                        print(l)
    except Error as e:
        print("TODO: REMOVE ME; Exception: " + str(e))
        pass

def process_string_message(jsonpayload, filename):

    try:
        msg = base64.b64decode(jsonpayload['data']).decode('utf-8')
        jsonpayload['data'] = msg
        jsonpayload['servertimestampUTC'] = datetime.datetime.utcnow().isoformat()
        decode = json.dumps(jsonpayload, ensure_ascii=False)
        if args.verbose:
            print(decode)
        with open(filename, 'a') as f:
           f.write(decode+'\n')

    except:
        pass

def on_message(client, userdata, msg):
    try:
        filename = args.output
        if not filename:
            filename = 'data' + datetime.datetime.utcnow().strftime('%Y%m%d') + '.json'
        filename    = os.path.join(args.output_dir, filename)
        print("TODO: REMOVE ME: payload: " + msg.payload.decode('utf-8'))
        jsonpayload = json.loads(msg.payload.decode('utf-8'))
        if  base64.b64decode(jsonpayload['data'])[0] == 0xc1:
            process_binary_message(jsonpayload, filename)
        else:
            process_string_message(jsonpayload, filename)

    except:
        pass
        
        
# Create ouptut directory if we need to
if args.output_dir and not os.path.exists(args.output_dir):
    os.makedirs(args.output_dir)

client            = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set('loraroot', password='loraroot')

client.connect("localhost", 1883, 60)
client.loop_forever()
