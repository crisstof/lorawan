import argparse
import json
import copy


def flatten_dict(d, parent_key = ''):
    items = []
    for k, v in d.items():
        try:
            items.extend(flatten_dict(v, '%s%s-' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)
    
    
def flatten_dict_and_vlists(d, parent_key = ''):
    items = []
    for k, v in d.items():
        try:
            if isinstance(v, list):
                for l in v: items.extend(flatten_dict_and_vlists(l, '%s%s-' % (parent_key, k)).items())
            else:
                items.extend(flatten_dict_and_vlists(v, '%s%s-' % (parent_key, k)).items())
        except AttributeError:
            items.append(('%s%s' % (parent_key, k), v))
    return dict(items)
    
    
def process_line(line, data_no_list, data_flatten, sort_keys = False):
    res = []
    
    if isinstance(line, dict):
        js = line
    else:
        # Parse JSON
        js = json.loads(line)
    
    # Remove data key and value from dictionnary before flattening it
    try:
        data = js['data']
        del    js['data']
    except ValueError:
        # There is no 'data' field.
        return res
        
    # Flatten remaining JSON
    #flatten_js = flatten_dict(data)
    flatten_js = flatten_dict_and_vlists(js)
    
    # Now put data back in, either as a list or as multiple lines
    if isinstance(data, list) and data_no_list:
        for d in data:
            # Flatten the data if we are asked to
            if isinstance(d, dict) and data_flatten:
                d = flatten_dict(d, 'data-')
                #flatten_js.update(d)
                js_copy = copy.deepcopy(flatten_js)
                js_copy.update(d)
                res.append(json.dumps(js_copy, ensure_ascii = False))
            else:
                flatten_js['data'] = d
                res.append(json.dumps(flatten_js, ensure_ascii = False))
    else:
        # Flatten the data if we are asked to
        if isinstance(data, dict) and data_flatten:
            data = flatten_dict(data, 'data-')
            flatten_js.update(data)
        else:
            flatten_js['data'] = data
        res.append(json.dumps(flatten_js, ensure_ascii = False, sort_keys = sort_keys))
    return res


def main():
    parser = argparse.ArgumentParser("Flatten a MQTT JSON")
    parser.add_argument('json_file',      metavar = 'JSON', help = 'The JSON file to process')
    parser.add_argument('--data-no-list', default = False, action = 'store_true', help = "The data field cannot contain a list; a single JSON line can produce several output JSON lines")
    parser.add_argument('--data-flatten', default = False, action = 'store_true', help = "Flatten the JSON data field")
    args = parser.parse_args()  
    
    with open(args.json_file, 'r') as f:
        for line in f:
            try:
                lines = process_line(line, args.data_no_list, args.data_flatten)
                for l in lines: 
                    if l: print(l)
            except ValueError:
                pass

    
if __name__ == "__main__":
    main()
