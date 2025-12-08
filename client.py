import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_ip = input("Enter Server IP: ")
port = 5678

try:
    s.connect((server_ip, port))
    print("Connected! Waiting for server to start the chat...")

    while True:
        data = s.recv(1024)
        if not data:
            print("Server disconnected.")
            break

        server_msg = data.decode("utf-8")
        print(f"[Server]: {server_msg}")

        if server_msg.lower() == "exit":
            print("Server ended the chat.")
            break

        my_message = input("[Client] You: ")
        s.sendall(my_message.encode("utf-8"))

        if my_message.lower() == "exit":
            break

except ConnectionRefusedError:
    print("Could not connect. Check IP and run server first.")
finally:
    s.close()