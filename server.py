import socket
import threading
import pygame
import sys

# --- Network Setup (Initial) ---
host = socket.gethostbyname(socket.gethostname())
port = 5678
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((host, port))
server_socket.listen(1)

# Variables
conn = None
addr = None
running = True
connected = False

# --- Network Thread ---
def wait_for_connection():
    global conn, addr, connected
    print(f"Server IP: {host}. Waiting...")
    try:
        conn, addr = server_socket.accept()
        connected = True
        print(f"Connected to {addr}")
        receive_data() # Start listening for data immediately after connection
    except:
        pass

def receive_data():
    global running
    while running:
        try:
            data = conn.recv(1024).decode("utf-8")
            if not data: break
            print(f"Received: {data}")
        except:
            break

# Start waiting in background
thread = threading.Thread(target=wait_for_connection)
thread.daemon = True
thread.start()

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Server")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)

# --- Game Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    if not connected:
        # Show IP and waiting message
        text_ip = font.render(f"Server IP: {host}", True, (255, 255, 255))
        text_status = font.render("Waiting for client...", True, (200, 200, 200))
        screen.blit(text_ip, (50, 150))
        screen.blit(text_status, (50, 200))
    else:
        # Show Connected State
        screen.fill((0, 100, 0)) # Dark Green background
        text_conn = font.render(f"Connected to: {addr[0]}", True, (255, 255, 255))
        screen.blit(text_conn, (50, 180))

    pygame.display.flip()
    clock.tick(60)

if conn: conn.close()
server_socket.close()
pygame.quit()
sys.exit()