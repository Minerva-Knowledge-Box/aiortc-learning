import socket

s = socket.socket() # by defalt ipv4 ad tcp : server socket created
print("Socket Created")

# we need ip address and port number to bind this socket

HOST = "127.0.0.1"   # or "" to listen on all interfaces
PORT = 9999          # 1024–65535 is safe for user apps

s.bind((HOST,PORT))
s.listen(3) #the number (3) is called the backlog. It means: the maximum number of queued connections waiting to be accepte
print("wating for connection")

while True: #connection will running continuous 
    c, addr = s.accept() # I will accept the connection from client: it return two thing clint socket and address 
    name = c.recv(1024).decode()
    print("Connected with ", addr, "given message: ", name)
    c.send(bytes("Welcome to server",'utf-8'))
    c.close()