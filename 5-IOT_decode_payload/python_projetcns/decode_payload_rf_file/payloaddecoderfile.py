import sys
import json
import argparse
import inspect
import os

# Import stuff common to all tools
if '..' not in sys.path:
    sys.path.insert(0, '..') 
import tools_common  

# Now import the codecs
tools_common.update_path_to_get_module('payloadcodecs')
import payloadcodecs.cnssrf.frame as cnssrf_frame


def process_payload(payload):
    print("*****payload")
    print(payload)
    payload = bytes.fromhex(payload)  # Convert hexas string to bytes array
    print("*****payload convert bytes array")
    print(payload)
    res     = cnssrf_frame.decode_payload(payload)
    print(json.dumps(res, sort_keys = True, indent = 2, ensure_ascii = False))


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser("ConnecS RF payload decoder")
    parser.add_argument('files', metavar = "FILE", nargs = '+',
                        help = "File(s) containing RF payload data.")
    args = parser.parse_args()

    # Go through the files
    for filename in args.files:
        with open(filename, 'r') as f:
            for line in f:
                process_payload(line.strip())

if __name__ == "__main__":
    main() 
