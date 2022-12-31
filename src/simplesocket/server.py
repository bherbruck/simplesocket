import logging
from socket import socket as Socket
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn

from event_handler import EventHandler
from util.receive_data import receive_data
from util.decode_data import decode_data


logger = logging.getLogger(__name__)


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass


class EventServer(ThreadedTCPServer, EventHandler):
    def __init__(self, port=3000, *args, **kwargs):
        # this is why I hate OOP/inheritance
        ThreadedTCPServer.__init__(
            self, ("", port), EventServerHandler, *args, **kwargs
        )
        EventHandler.__init__(self)
        self.port = port
        self.sockets: list[Socket] = []
        self.allow_reuse_address = True
        self.allow_reuse_port = True

    def send(self, socket: Socket, event: str, payload: str):
        socket.sendall(f"{event} {payload}".encode("utf-8").strip() + b"\n")

    def broadcast(self, event: str, payload: str):

        for socket in self.sockets:
            self.send(socket, event, payload)

    def close(self):
        self.shutdown()
        self.server_close()

    def start(self):
        self.serve_forever()
        self.allow_reuse_address = True
        self.allow_reuse_port = True


class EventServerHandler(BaseRequestHandler):
    def handle_missing_event(self, socket: Socket):
        self.server.send(socket, "error", "Missing event")

    def handle_invalid_event(self, socket: Socket):
        self.server.send(socket, "error", "Invalid event")

    def handle_payload():
        pass

    def handle(self):
        server: EventServer = self.server
        socket: Socket = self.request

        server.sockets.append(socket)

        for handler in server.connect_handlers:
            handler(socket)

        while True:
            try:
                data = receive_data(socket)
                if not data:
                    break

                event, payload = decode_data(data)
                response = server.event_handlers[event](socket, payload)
                if response is not None:
                    server.send(socket, event, response)

            except ValueError:
                self.handle_missing_event(socket)
                continue
            except KeyError:
                self.handle_invalid_event(socket)
                continue
            except Exception as e:
                logger.exception(e)

        server.sockets.remove(socket)

        for handler in server.disconnect_handlers:
            handler(socket)
