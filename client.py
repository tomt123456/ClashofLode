import socket
import pygame as pg



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_ip = input("Zadajte Server IP: ")
port = 5678

pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((1280, 720))
pg.display.set_caption("Clash of Loďe")

try:
    clock.tick(60)
    s.connect((server_ip, port))
    print("Pripojené")
    while True:
        data = s.recv(1024)
        if not data:
            print("Server odpojený.")
            break
        server_msg = data.decode("utf-8")
        print(f"[Server]: {server_msg}")
        if server_msg.lower() == "exit":
            print("Server ukončil chat.")
            break
        my_message = input("[Client] You: ")
        s.sendall(my_message.encode("utf-8"))
        if my_message.lower() == "exit":
            break

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
except ConnectionRefusedError:
    print("Nepodarilo sa pripojiť na server.")
finally:
    s.close()