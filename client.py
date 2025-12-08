import socket
import threading
import pygame
import sys

# --- Network Configuration ---
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = input("Enter Server IP: ")
port = 5678

try:
    s.connect((server_ip, port))
    print("Connected to server!")
except Exception as e:
    print(f"Could not connect: {e}")
    sys.exit()

running = True


# --- Network Thread Function ---
def receive_data():
    global running
    while running:
        try:
            data = s.recv(1024).decode("utf-8")
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
pygame.display.set_caption("Client (Blank)")
clock = pygame.time.Clock()

# --- Game Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Send data example:
    # s.sendall("Hello from client".encode("utf-8"))

    # Drawing
    screen.fill((0, 0, 0))  # Black background

    pygame.display.flip()
    clock.tick(60)

s.close()
pygame.quit()
sys.exit()