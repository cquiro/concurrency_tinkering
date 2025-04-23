from socket import socket, create_server

BUFFER_SIZE = 1024
ADDRESS = ("127.0.0.1", 12345)

class Server:
    def __init__(self) -> None:
        try:
            print(f"Starting up at {ADDRESS}")
            self.server_socket: socket = create_server(ADDRESS)
        except OSError:
            self.server_socket.close()
            print("\nServer stopped.")

    def accept(self) -> socket:
        conn, client_address = self.server_socket.accept()
        print(f"Connected to {client_address}")
        return conn

    def serve(self, conn: socket) -> None:
        try:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                try:
                    order = int(data.decode())
                    response = f"Thank you for ordering {order} pizzas!\n"
                except ValueError:
                    response = "Wrong number of pizzas, please try again\n"
                print(f"Sending message to {conn.getpeername()}")
                conn.send(response.encode())

        finally:
            print(f"Connection with {conn.getpeername()} has been closed")
            conn.close()

    def start(self) -> None:
        print("Server listening for incoming connections")
        try:
            while True:
                conn = self.accept()
                self.serve(conn)
        finally:
            self.server_socket.close()
            print("\nServer stopped.")

if __name__ == "__main__":
    server = Server()
    server.start()


