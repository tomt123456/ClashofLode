import socket, random
import threading
def receiveData(sock):
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            print(data.decode("utf-8"))
        except:
            pass

serverIP = input("zadaj IP serevra: ")
server = (str(serverIP), 5678)

host = socket.gethostbyname(socket.gethostname())
port = random.randint(6000, 10000)
print("client IP " + str(host) + " port " + str(port))
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind((host, port))
name = input("zadaj svoj nick: ")
while True:
    data = '['+name+']: ' + input()
    s.sendto(data.encode("utf-8"), server)