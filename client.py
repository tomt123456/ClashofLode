import socket
import threading
import pygame
import sys

# --- Pygame Setup ---
pygame.init()
screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Client")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)

# Variables
user_text = ''
input_rect = pygame.Rect(200, 150, 200, 32)
color_active = pygame.Color('lightskyblue3')
color_passive = pygame.Color('gray15')
color = color_passive
active = False
running = True
connected = False
connect_error = ""

# Network variables
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
port = 5678


# --- Network Thread ---
def receive_data():
    global running
    while running:
        try:
            data = s.recv(1024).decode("utf-8")
            if not data: break
            print(f"Received: {data}")
        except:
            break


def attempt_connection(ip_addr):
    global connected, connect_error
    try:
        connect_error = "Connecting..."
        s.connect((ip_addr, port))
        connected = True

        # Start listening thread
        thread = threading.Thread(target=receive_data)
        thread.daemon = True
        thread.start()
    except Exception as e:
        connect_error = "Failed. Try again."
        print(e)


# --- Game Loop ---
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not connected:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        # Attempt connection on Enter
                        attempt_connection(user_text)
                    elif event.key == pygame.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

    screen.fill((0, 0, 0))

    if not connected:
        # Draw Instructions
        label = font.render("Enter Server IP and press Enter:", True, (255, 255, 255))
        screen.blit(label, (150, 100))

        # Draw Input Box
        if active:
            color = color_active
        else:
            color = color_passive

        pygame.draw.rect(screen, color, input_rect, 2)
        text_surface = font.render(user_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
        input_rect.w = max(200, text_surface.get_width() + 10)

        # Draw Error/Status Message
        if connect_error:
            err_surf = font.render(connect_error, True, (255, 100, 100))
            screen.blit(err_surf, (200, 200))

    else:
        # Show Connected State
        screen.fill((0, 0, 100))  # Dark Blue background
        text_conn = font.render("Connected to Server!", True, (255, 255, 255))
        screen.blit(text_conn, (150, 180))

    pygame.display.flip()
    clock.tick(60)

s.close()
pygame.quit()
sys.exit()