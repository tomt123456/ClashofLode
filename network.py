import socket
import threading

PORT = 5678


class Network:
    def __init__(self):
        self.sock = None
        self.conn = None
        self.is_host = False
        self.connected = False
        self.running = True

    def start_host(self):
        self.is_host = True

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((local_ip, PORT))
        self.sock.listen(1)

        print(f"[HOST] Listening on {local_ip}:{PORT}")

        def accept_thread():
            try:
                self.conn, addr = self.sock.accept()
                self.connected = True
                print(f"[HOST] Client connected: {addr}")
                self.listen_for_data(self.conn)
            except Exception:
                pass

        threading.Thread(target=accept_thread, daemon=True).start()
        return local_ip

    def start_client(self, target_ip: str) -> bool:
        self.is_host = False
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((target_ip, PORT))
            self.connected = True
            print(f"[CLIENT] Connected to {target_ip}")

            threading.Thread(target=lambda: self.listen_for_data(self.sock), daemon=True).start()
            return True
        except Exception as e:
            print(f"[CLIENT] Error: {e}")
            return False

    def listen_for_data(self, socket_obj):
        while self.running:
            try:
                data = socket_obj.recv(1024).decode("utf-8")
                if not data:
                    # remote closed connection
                    self.connected = False
                    break
                print(f"Received: {data}")
            except Exception:
                # on error, mark disconnected but don't stop the whole app
                self.connected = False
                break

    def send(self, msg: str):
        try:
            if self.is_host and self.conn:
                self.conn.sendall(msg.encode())
            elif (not self.is_host) and self.sock:
                self.sock.sendall(msg.encode())
        except Exception:
            # mark disconnected but avoid shutting down the entire Network controller
            print(f"[NETWORK] send error, disconnecting")
            self.connected = False
            try:
                if self.sock:
                    self.sock.close()
            except Exception:
                pass
            try:
                if self.conn:
                    self.conn.close()
            except Exception:
                pass

    def close(self):
        self.running = False
        try:
            if self.sock:
                self.sock.close()
        finally:
            self.sock = None

        try:
            if self.conn:
                self.conn.close()
        finally:
            self.conn = None