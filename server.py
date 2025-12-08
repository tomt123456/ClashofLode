import socket
import pygame as pg


# initialize pygame
pg.init()
clock = pg.time.Clock()
screen = pg.display.set_mode((1280, 720))
pg.display.set_caption("Clash of Loďe")

running = True


host = socket.gethostbyname(socket.gethostname())
print(f"Server IP: {host}")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 5678
s.bind((host, port))
s.listen(1)
print(f"Waiting for client on port {port}...")
conn, addr = s.accept()
print(f"Client connected: {addr}")

try:
    clock.tick(60)
    while running:
        my_message = input("[Server] You: ")
        conn.sendall(my_message.encode("utf-8"))

        if my_message.lower() == "exit":
            break

        data = conn.recv(1024)
        if not data:
            print("Client disconnected.")
            break

        print(f"[Client]: {data.decode('utf-8')}")

        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False

except KeyboardInterrupt:
    print("\nClosing connection...")
finally:
    conn.close()
    s.close()