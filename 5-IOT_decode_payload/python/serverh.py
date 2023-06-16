#coding:utf-8
import socket

host, port = ('', 5566)
#server_port = 5566

#socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#socket.bind((host, port))
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
print("Le serveur est démarré...")
server_socket.listen()	
conn, address = server_socket.accept()

while (1):
 
  print("En écoute...")
  data = conn.recv(1024)
  data = data.decode("utf8")
  print(data)
  message = input(">> ")
  conn.send(message.encode())
  
  if(message == 'q'):
    conn.close()
    server_socket.close()
  

