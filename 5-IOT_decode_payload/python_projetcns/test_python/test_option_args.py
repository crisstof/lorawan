import sys
import json
import argparse
import inspect
import os

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser("on peut mettre des arguments")
    #parser.add_argument('-p', '--port',  default = None)
    parser.add_argument('files', metavar = "FILE", nargs = '+',
                       help = "File(s) containing RF payload data.")
     
    args = parser.parse_args()
    
   
   #python .\test.py -p 8    
    print("******")
    #print(args.port)
    print("******")
    print(args.files)
    print("******")
    # Go through the files
    
    for filename in args.files:
        with open(filename, 'r') as f:
            for line in f:
                #process_payload(line.strip())
                print(line.strip())
    
if __name__ == "__main__":
    main() 




 