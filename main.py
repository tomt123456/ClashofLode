import socket
import threading
import pygame
import sys

# --- Constants & Config ---
PORT = 5678
WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 100, 0)
BLUE = (0, 0, 100)
BUTTON_COLOR = (50, 150, 255)
BUTTON_HOVER = (80, 180, 255)

# --- Global Network Variables ---
sock = None  # Will hold either server or client socket
conn = None  # Only used if Host (to hold client connection)
is_host = False
connected = False
running = True


# --- Network Functions ---

def start_host():
    """Initializes Server Logic"""
    global sock, conn, connected, is_host
    is_host = True

    # Get local IP
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((local_ip, PORT))
    sock.listen(1)

    print(f"[HOST] Listening on {local_ip}:{PORT}")

    def accept_thread():
        global conn, connected
        try:
            conn, addr = sock.accept()
            connected = True
            print(f"[HOST] Client connected: {addr}")
            listen_for_data(conn)
        except:
            pass

    threading.Thread(target=accept_thread, daemon=True).start()
    return local_ip


def start_client(target_ip):
    """Initializes Client Logic"""
    global sock, connected, is_host
    is_host = False

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, PORT))
        connected = True
        print(f"[CLIENT] Connected to {target_ip}")

        # Start listening immediately
        threading.Thread(target=lambda: listen_for_data(sock), daemon=True).start()
        return True
    except Exception as e:
        print(f"[CLIENT] Error: {e}")
        return False


def listen_for_data(socket_obj):
    """Generic listener for both Host and Client"""
    global running
    while running:
        try:
            data = socket_obj.recv(1024).decode("utf-8")
            if not data: break
            print(f"Received: {data}")
        except:
            break


# --- GUI Components ---

class Button:
    def __init__(self, x, y, w, h, text):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.is_hovered = False

    def draw(self, screen, font):
        color = BUTTON_HOVER if self.is_hovered else BUTTON_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)

    def is_clicked(self, event):
        return self.is_hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1


# --- Main Application ---

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Network Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)
title_font = pygame.font.Font(None, 50)

# States
STATE_MENU = 0
STATE_HOSTING = 1
STATE_JOINING = 2
STATE_GAME = 3

current_state = STATE_MENU

# UI Elements
btn_host = Button(100, 200, 150, 50, "HOST")
btn_join = Button(350, 200, 150, 50, "JOIN")

# Input Box Variables
user_ip = ""
input_rect = pygame.Rect(200, 150, 200, 32)
input_active = False
connection_status = ""
host_ip_display = ""

while running:
    events = pygame.event.get()
    mouse_pos = pygame.mouse.get_pos()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

    # --- STATE LOGIC ---

    # 1. MAIN MENU
    if current_state == STATE_MENU:
        screen.fill(BLACK)

        # Title
        title = title_font.render("Select Mode", True, WHITE)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))

        # Buttons
        btn_host.check_hover(mouse_pos)
        btn_join.check_hover(mouse_pos)
        btn_host.draw(screen, font)
        btn_join.draw(screen, font)

        for event in events:
            if btn_host.is_clicked(event):
                current_state = STATE_HOSTING
                host_ip_display = start_host()

            if btn_join.is_clicked(event):
                current_state = STATE_JOINING

    # 2. HOSTING SCREEN (Waiting)
    elif current_state == STATE_HOSTING:
        if connected:
            current_state = STATE_GAME

        screen.fill(GREEN)
        msg1 = font.render("Waiting for player...", True, WHITE)
        msg2 = font.render(f"Your IP: {host_ip_display}", True, WHITE)
        screen.blit(msg1, (50, 150))
        screen.blit(msg2, (50, 200))

    # 3. JOINING SCREEN (Input IP)
    elif current_state == STATE_JOINING:
        if connected:
            current_state = STATE_GAME

        screen.fill(GRAY)

        # Input Logic
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False

            if event.type == pygame.KEYDOWN and input_active:
                if event.key == pygame.K_RETURN:
                    connection_status = "Connecting..."
                    success = start_client(user_ip)
                    if not success:
                        connection_status = "Failed. Try again."
                elif event.key == pygame.K_BACKSPACE:
                    user_ip = user_ip[:-1]
                else:
                    user_ip += event.unicode

        # Draw UI
        label = font.render("Enter Host IP:", True, WHITE)
        screen.blit(label, (200, 120))

        color = BUTTON_HOVER if input_active else BLACK
        pygame.draw.rect(screen, color, input_rect, 2)
        text_surf = font.render(user_ip, True, WHITE)
        screen.blit(text_surf, (input_rect.x + 5, input_rect.y + 5))

        if connection_status:
            status_surf = font.render(connection_status, True, (255, 200, 200))
            screen.blit(status_surf, (200, 200))

    # 4. GAME SCREEN (Both connected)
    elif current_state == STATE_GAME:
        bg_color = GREEN if is_host else BLUE
        screen.fill(bg_color)

        role_text = "HOST" if is_host else "CLIENT"
        txt = title_font.render(f"GAME ON! Role: {role_text}", True, WHITE)
        screen.blit(txt, (50, 150))

        # Example: Send "Ping" on spacebar
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                msg = f"Ping from {role_text}"
                try:
                    if is_host and conn:
                        conn.sendall(msg.encode())
                    elif not is_host and sock:
                        sock.sendall(msg.encode())
                except:
                    running = False

    pygame.display.flip()
    clock.tick(60)

# Cleanup
if sock: sock.close()
if conn: conn.close()
pygame.quit()
sys.exit()