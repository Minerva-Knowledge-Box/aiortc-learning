import socket

c = socket.socket()
HOST, PORT = "127.0.0.1", 9999
c.connect((HOST, PORT))

name = input("Enter your name: ")
c.send(name.encode("utf-8"))            # send once
print(c.recv(1024).decode("utf-8"))     # read once
c.close()
