from struct import *

DATA_TYPE_NAME = "VoltageV"
DATA_TYPE_ID   = 0x0c

payload = b'0011 0001 0011 0000' #12592

depacker       = Struct('<h')
print(payload[0:2]) #=>b'00'

value = depacker.unpack(payload[0:2])
print(value)#=>(12336,)

packed = pack('i 4s f', 10, b'John', 2500)
print(packed)#=> b'\n\x00\x00\x00John\x00@\x1cE'
packed = b'\n\x00\x00\x00John\x00@\x1cE'

unpacked = unpack('i 4s f', packed)
print(unpacked)#=>(10, b'John', 2500.0)



#unpacked = struct.unpack('i 4s f',10, b'John', 2500)
#print(unpacked)