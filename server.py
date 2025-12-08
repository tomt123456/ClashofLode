import socket
import threading
import pygame
import sys

# --- Network Configuration ---
host = socket.gethostbyname(socket.gethostname())
print(f"Server IP: {host}")
port = 5678

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

print("Waiting for client to connect...")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

running = True


# --- Network Thread Function ---
def receive_data():
    global running
    while running:
        try:
            data = conn.recv(1024).decode("utf-8")
            if not data:
                break

            # Placeholder for handling received data
            print(f"Received: {data}")
        except:
            break


# Start the listener thread
thread = threading.Thread(target=receive_data)
thread.daemon = True
thread.start()

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Server (Blank)")
clock = pygame.time.Clock()

# --- Game Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Drawing
    screen.fill((0, 0, 0))  # Black background

    pygame.display.flip()
    clock.tick(60)

conn.close()
server_socket.close()
pygame.quit()
sys.exit()