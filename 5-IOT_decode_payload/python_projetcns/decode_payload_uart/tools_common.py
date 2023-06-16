# -*- coding: utf-8

from __future__ import print_function

import sys
import os.path
import inspect


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
        print("Failed to findeee path for module '{m}'.".format(m = module_name), file = sys.stderr)
		
		
        if required:
            sys.exit(1)
        return False
        
    if libs_path not in sys.path:
        sys.path.insert(0, libs_path)   
    return True
