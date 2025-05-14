import select
import socket
from socket import socket, create_server
from typing import Callable, Union, Tuple

Mask = int
Action = Union[Callable[[socket], None], Tuple[Callable[[socket, str], None], str]]

class EventLoop:
    def __init__(self) -> None:
        self.writers = {}
        self.readers = {}

    def register_event(self, source: socket, event: Mask, action: Action) -> None:
        key = source.fileno()
        if event & select.POLLIN:
            self.readers[key] = (source, event, action)
        elif event & select.POLLOUT:
            self.writers[key] = (source, event, action)

    def unregister_event(self, source: socket) -> None:
        key = source.fileno()
        if self.readers.get(key):
            del self.readers[key]
        if self.writers.get(key):
            del self.writers[key]

    def run_forever(self) -> None:
        while True:
            readers, writers, _ = select.select(
                self.readers, self.writers, [])

            for reader in readers:
                source, event, action = self.readers.pop(reader)
                action(source)

            for writer in writers:
                source, event, action = self.writers.pop(writer)
                action, msg = action
                action(source, msg)

BUFFER_SIZE = 1024
ADDRESS = ("127.0.0.1", 12345)

class Server:
    def __init__(self, event_loop: EventLoop) -> None:
        self.event_loop = event_loop
        try:
            print(f"Starting up at: {ADDRESS}")
            self.server_socket = create_server(ADDRESS)
            self.server_socket.setblocking(False)
        except OSError:
            self.server_socket.close()
            print(f"\nServer stopped.")

    def _on_accept(self, _: socket) -> None:
        try:
            conn, client_address = self.server_socket.accept()
        except BlockingIOError:
            return
        conn.setblocking(False)
        print(f"Connected to {client_address}")
        self.event_loop.register_event(conn, select.POLLIN, self._on_read)
        self.event_loop.register_event(self.server_socket, select.POLLIN, self._on_accept)

    def _on_read(self, conn: socket) -> None:
        try:
            data = conn.recv(BUFFER_SIZE)
        except BlockingIOError:
            return
        if not data:
            self.event_loop.unregister_event(conn)
            print(f"Connection with {conn.getpeername()} has been closed")
            conn.close()
            return
        message = data.decode().strip()
        self.event_loop.register_event(conn, select.POLLOUT, (self._on_write, message))

    def _on_write(self, conn: socket, message: bytes) -> None:
        try:
            order = int(message)
            response = f"Thank you for ordering {order} pizzas!\n"
        except ValueError:
            response = "Wrong number of pizzas, please try again\n"
        print(f"Sending message to {conn.getpeername()}")
        try:
            conn.send(response.encode())
        except BlockingIOError:
            return
        self.event_loop.register_event(conn, select.POLLIN, self._on_read)

    def start(self) -> None:
        print("Server listening for incoming connections")
        self.event_loop.register_event(self.server_socket, select.POLLIN, self._on_accept)

if __name__ == "__main__":
    event_loop = EventLoop()
    Server(event_loop = event_loop).start()
    event_loop.run_forever()


