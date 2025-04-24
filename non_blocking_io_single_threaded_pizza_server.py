import typing as T
from socket import socket, create_server

BUFFER_SIZE = 1024
ADDRESS = ("127.0.0.1", 12345)

class Server:
    clients: T.Set[socket] = set()

    def __init__(self) -> None:
        try:
            print(f"Starting up at: {ADDRESS}")
            self.server_socket = create_server(ADDRESS)
            self.server_socket.setblocking(False)
        except OSError:
            self.server_socket.close()
            print("\nServer stopped.")

    def accept(self) -> None:
        try:
            conn, address = self.server_socket.accept()
            print(f"Connected to {address}")
            conn.setblocking(False)
            self.clients.add(conn)
        except BlockingIOError:
            pass

    def serve(self, conn: socket) -> None:
        try:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    print(f"Connection with {conn.getpeername()} has been closed.")
                    conn.close()
                    self.clients.remove(conn)
                    break
                try:
                    order = int(data.decode())
                    response = f"Thank you for ordering {order} pizzas!\n"
                except ValueError:
                    response = "Wrong number of pizzas, please try again\n"
                print(f"Sending message to {conn.getpeername()}")
                conn.send(response.encode())
        except BlockingIOError:
            pass
        except OSError as e:
            print(f"Error with {conn.getpeername()}: {e}")
            conn.close()
            self.clients.remove(conn)


    def start(self) -> None:
        print("Server listening for incoming connections")
        try:
            while True:
                self.accept()
                for conn in self.clients.copy():
                    self.serve(conn)
        finally:
            self.server_socket.close()
            print("\nServer stopped.")

if __name__ == "__main__":
    server = Server()
    server.start()

