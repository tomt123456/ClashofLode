import socket

host = socket.gethostbyname(socket.gethostname())
print("Server bude na IP", host)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 5678
s.bind((host, port))
clients = set()
print("Server bezi na porte", port)

while True:
    data, addr = s.recvfrom(1024)
    clients.add(addr)
    data = data.decode("utf-8")
    print(str(addr)+data)
    for c in clients:
        if c != addr:
            s.sendto(data.encode("utf-8"), c)