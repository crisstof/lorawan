import sys      #paramètre et fonction propres au system [sys.argv}
import json     #api encode/decode json
import argparse #facilite l'écriture d'interfaces de ligne de commande conviviale
import inspect  #méthode pour founir des informations sur class fonctin objet
import os       #permet d'interagir avec le système os et acces aux infos system
import subprocess#gestion génère de nouveau processus remplace des modules ou fonctions plus anciennes
import site     #configuration hook crochet
import importlib#permet de charger des modules au fur et à mesure ou utilise des obj perso
from importlib import reload#recharge un module précédemment importé par le programme
 

# Import stuff common to all tools
if '..' not in sys.path:
    sys.path.insert(0, '..') #ajoute .. retour dans le path en position 0 début
	
import tools_common

# Now import the codecs
tools_common.update_path_to_get_module('payloadcodecs')

import payloadcodecs.cnssrf.frame as cnssrf_frame


# Check if we are running on Windows
running_on_Windows = (sys.platform == 'Windows' or sys.platform == 'win32')
to_ascii           = running_on_Windows

serial_port  = None
key_listener = None


EXIT_CODE_OK             = 0
EXIT_CODE_STOP           = 1
EXIT_CODE_NO_SERIAL_PORT = 2
EXIT_CODE_IMPORT_ERROR   = 3


def exit_program(exit_code):
    global serial_port
    global key_listener
    
    if serial_port:  serial_port .close()
    if key_listener: key_listener.stop()
        
    if exit_code == EXIT_CODE_STOP:
        print("Bye! See you soon...")
        
    os._exit(exit_code)

#detecte et propose d'installer les packages manquant
def install_and_import_module(package_name, confirm, required, import_name = None):
    if not import_name:
        import_name = package_name
    
    # Print some user messages
    required_msg = "optionnal"
    if required:
        required_msg = "required"
    print("Python module '{0}' is not installed on your computer; this module is {1}.".format(
        package_name, required_msg), 
        file = sys.stderr)
    print("Your computer must be connected to Internet to install Python modules.")
    input("Press 'Enter' key.")
    
    # Ask for confirmation
    if confirm:
        c = ''
        while len(c) != 1:
            c = input("Do you wish to install '{0}' module [Y/n]?:".format(package_name))
        if c == 'n' or c == 'N':
            return False
    
    # Install mosule using pip
    print("Installing '{0}' Python module...".format(package_name))
    subprocess.call([sys.executable, '-m', 'pip', 'install', package_name])

    # update sys.path; just in case.
    reload(site)
    
    # Import module
    try:
        importlib.invalidate_caches()
        importlib.import_module(import_name)
    except ImportError:
        print("ERROR: failed to import '{0}' Python module. Try to restart the application.".format(package_name), 
              file = sys.stderr)
        exit_program(EXIT_CODE_IMPORT_ERROR)
        
    return True
    

# Import pyserial
try:
    import serial 
except ImportError:
    install_and_import_module('pyserial', False, True, 'serial')
import serial.tools.list_ports
    
     
# Import pynput
has_pynput  = False
if running_on_Windows:
    try:
        import pynput
        has_pynput = True
    except ImportError:
        has_pynput = install_and_import_module('pynput', True, False)
        has_pynput
                
        if not has_pynput:
            print(
        """WARNING: Failed to import 'pynput' module.
This module is not needed but without it you cannot exit program using a key press.""",
                file = sys.stderr)  
    
 #decode les données du port série   
def bytes_to_string(b):

    if to_ascii:
        return b.decode('ascii', 'replace')
        
    s = None
    try:
        s = b.decode('utf-8')
    except UnicodeDecodeError:
        pass
    if not s:
        try:
            s = b.decode('cp1252')
        except UnicodeDecodeError:
            pass
    if not s:
        try:
            s = b.decode('latin-1')
        except UnicodeDecodeError:
            pass
    if not s:
        try:
            s = b.decode('iso8859-15')
        except UnicodeDecodeError:
            pass
    if not s:
        print("Error: can't decode log line.")
        return ''
        
    return s

 #appelle la fonction frame et depuis frame:
#frame appelle les datatypes pour décodé le payload 
def process_log_line(line):
    line = bytes_to_string(line).rstrip('\r\n') #transforme les bytes en string et on enlève le \r\n
    print(line)
    if "|CNSSRF payload:" in line:
        payload_index = line.rfind(':')
        if payload_index == -1:
            # This should not happen
            pass
        payload_index = payload_index + 1;#on positionne le curseur de lecture au niveau du payload+1 pour l'espace
        while line[payload_index] in [' ', '/t']:
            payload_index = payload_index + 1
        payload = line[payload_index : ]  # +1 to remove space character after colon
        print(payload)
        #transforme notre string payload pour créer un objets bytes à partir 
        #d'une chaîne de chiffres hexadécimaux
        payload = bytes.fromhex(payload)  # Convert hexas string to bytes array
        res     = cnssrf_frame.decode_payload(payload)
        print(json.dumps(res, sort_keys = True, indent = 2, ensure_ascii = to_ascii))
    
    
def get_port(port):
    if port is not None:
        return port
    
    # Go through the ports to see if there is only one candidate
    ports          = serial.tools.list_ports.comports();
    nb_candidates  = 0
    last_candidate = None
    for port in ports:
        if 'ttyUSB' in port.device or 'COM' in port.device:
            nb_candidates  = nb_candidates + 1
            last_candidate = port.device
    if nb_candidates == 0:
        print("""No serial port has been detected.
Make sure that your adaptator is plugged in or use the -p (--port) command line switch to specify the port to use.""",
            file = sys.stderr)
        exit_program(EXIT_CODE_NO_SERIAL_PORT)
    elif nb_candidates == 1:
        return last_candidate
    
    # More than one candidate; display a list for the user to choose from
    print("Choose port from this list:")
    i = 0
    for port in ports:
        print("{0}: {1}".format(i, port.device))
        i = i + 1
    i = int(input("Number of port to use: "))
    return ports[i].device
    
    
def key_press(key):
    if key.char == 'q':
        exit_program(EXIT_CODE_STOP)
    
    
def main():
    global serial_port
    global key_listener
    
    # Parse command line arguments
    parser = argparse.ArgumentParser("ConnecSenS logs serial console")
    parser.add_argument('-p', '--port',  default = None)
    parser.add_argument('-s', '--speed', default = 115200, type = int)
    args = parser.parse_args()
    
    port = get_port(args.port)
    
    # Build exit message
    msg = "'Ctrl+C'"
    if running_on_Windows:
        msg = "'Ctrl+Break' ('Ctrl+Pause' on French keyboard)"
    if has_pynput:
        msg = "'q' key or " + msg
    print("Press " + msg + " key(s) to quit application.")
            
    # Start key listener if ther is one
    if has_pynput:
        key_listener = pynput.keyboard.Listener(on_press = key_press)
        key_listener.start()
        
    print("Serial port '{0}' opened at {1} bauds".format(port, args.speed))
    serial_port = serial.Serial(port, args.speed)
    try:
        while True:
            process_log_line(serial_port.readline())
    except KeyboardInterrupt:
        exit_program(EXIT_CODE_STOP)
    exit_program(EXIT_CODE_OK)
    
    
    
if __name__ == "__main__":
	main()
os.system("pause")
	
	
