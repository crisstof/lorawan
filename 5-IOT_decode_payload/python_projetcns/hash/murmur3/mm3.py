# -*- coding: utf-8 -*-



from __future__ import print_function

import sys
import argparse


CONNECSENS_SEED_32 =  0x434E5353


def murmur3_littleendian_32(data, seed = 0):
    """Little endian implementation of the 32 bits Murmur3 hash 
    algorithm.
    
    Parameters:
        data The data to hash. MUST be NOT None.
        seed The seed value to use.
        
    Return the hash value.
    """
    c1 = 0xcc9e2d51
    c2 = 0x1b873593

    length = len(data)
    h1 = seed
    roundedEnd = (length & 0xfffffffc)  # round down to 4 byte block
    for i in range(0, roundedEnd, 4):
      # little endian load order
      k1 = (ord(data[i]) & 0xff) | ((ord(data[i + 1]) & 0xff) << 8) | \
           ((ord(data[i + 2]) & 0xff) << 16) | (ord(data[i + 3]) << 24)
      k1 *= c1
      k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17) # ROTL32(k1,15)
      k1 *= c2

      h1 ^= k1
      h1 = (h1 << 13) | ((h1 & 0xffffffff) >> 19)  # ROTL32(h1,13)
      h1 = h1 * 5 + 0xe6546b64

    # tail
    k1 = 0

    val = length & 0x03
    if val == 3:
        k1 = (ord(data[roundedEnd + 2]) & 0xff) << 16
    # fallthrough
    if val in [2, 3]:
        k1 |= (ord(data[roundedEnd + 1]) & 0xff) << 8
    # fallthrough
    if val in [1, 2, 3]:
        k1 |= ord(data[roundedEnd]) & 0xff
        k1 *= c1
        k1 = (k1 << 15) | ((k1 & 0xffffffff) >> 17)  # ROTL32(k1,15)
        k1 *= c2
        h1 ^= k1

    # finalization
    h1 ^= length

    # fmix(h1)
    h1 ^= ((h1 & 0xffffffff) >> 16)
    h1 *= 0x85ebca6b
    h1 ^= ((h1 & 0xffffffff) >> 13)
    h1 *= 0xc2b2ae35
    h1 ^= ((h1 & 0xffffffff) >> 16)

    return h1 & 0xffffffff
    
    

def mm3_32(data, seed = 0):
    """32 bits Murmur3 hash algorithm.
    
    WARNING: Only little-endian implementation is available.
    
    Parameters:
        data The data to hash. MUST be NOT None.
        seed The seed value to use.
        
    Return the hash value.
    """
    return murmur3_littleendian_32(data, seed)



def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser("Generate Murmur3 hashes")
    parser.add_argument(
        'data',  
        metavar = 'DATA', 
        help    = "The data to hash.")
    parser.add_argument(
        '-s', '--seed', 
        default = CONNECSENS_SEED_32, 
        help    = "Seed value")
    parser.add_argument(
        '-l', '--lower-case',
        default = False,
        action  = 'store_true',
        help    = "Print hash value in lower case.")
    args = parser.parse_args()

    # Get seed
    seed = args.seed
    if isinstance(seed, str):
        if seed.startswith('0x') or seed.startswith('0X'):
            seed = int(seed, 16)
        else:
            seed = int(seed)
    elif isinstance(seed, int):
        pass  # Nothing to do
    else:
        print(("Error: 'seed' parameter must be an integer or "
               "an hexadecimal value"),
               file = sys.stderr)
        
    # Compute hash
    h = mm3_32(args.data, seed)
    
    # Print HASH
    if args.lower_case: 
        print(format(h, '08x'))
    else:
        print(format(h, '08X'))


if __name__ == "__main__":
    main()
