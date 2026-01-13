import socket
import threading

class SocketListener:
    def __init__(self, host="localhost", port=5000, callback=None):
        """
        host: where the server listens (localhost)
        port: must match the C# client's port
        callback: function to call when a rotation value is received
        """
        self.host = host
        self.port = port
        self.callback = callback     # circular menu will pass a function here
        self.server_socket = None
        self.client_socket = None
        self.listening_thread = None
        self.running = False

    def start_server(self):
        """Starts the TCP server and begins listening for the C# client."""
        self.running = True

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)

        print(f"[PYTHON SERVER] Listening on {self.host}:{self.port} ...")

        # Accept client in a separate thread
        threading.Thread(target=self.accept_client, daemon=True).start()

    def accept_client(self):
        """Waits for the C# client to connect."""
        self.client_socket, addr = self.server_socket.accept()
        print(f"[PYTHON SERVER] Client connected from {addr}")

        # Start thread to receive messages
        self.listening_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.listening_thread.start()

    def receive_messages(self):
        """Continuously receive messages from the C# client."""
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    continue

                msg = data.decode().strip()

                # Expecting angle values like "132.5"
                print(f"[PYTHON SERVER] Received: {msg}")

                # Call the callback function (e.g., update the circular menu)
                if self.callback:
                    try:
                        angle = float(msg)
                        self.callback(angle)
                    except ValueError:
                        print("[ERROR] Received non-numeric message")

            except:
                print("[PYTHON SERVER] Error receiving message")
                break

    def stop(self):
        """Stops the server cleanly."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
