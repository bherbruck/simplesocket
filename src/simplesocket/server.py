"""EventServer"""

import logging
from socket import socket as Socket
from socketserver import BaseRequestHandler, TCPServer, ThreadingMixIn

from event_handler import EventHandler  # pylint: disable=import-error
from packet import Packet  # pylint: disable=import-error


logger = logging.getLogger(__name__)


# pylint: disable=missing-class-docstring
class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass


class EventServer(ThreadedTCPServer, EventHandler):
    """A server that can send and receive events"""

    def __init__(self, host="", port=3000):
        self.allow_reuse_address = True
        # this is why I hate OOP/inheritance
        ThreadedTCPServer.__init__(self, (host, port), EventServerHandler)
        EventHandler.__init__(self)
        self.host = host
        self.port = port
        self.sockets: dict[str, Socket] = {}

    def send(self, socket: Socket, event: str, message: str):
        """Send an event to a socket"""
        return Packet.send(socket, event, message)

    def broadcast(self, event: str, message: str):
        """Send an event to all sockets"""
        for socket in self.sockets.values():
            self.send(socket, event, message)

    def close(self):
        """Close all sockets and stop the server"""
        self.shutdown()
        self.server_close()

    def start(self):
        """Start the server"""
        self.serve_forever()


class EventServerHandler(BaseRequestHandler):
    """A handler for the EventServer"""

    def handle_missing_event(self, socket: Socket):
        """Handle a missing event"""
        self.server.send(socket, "error", "Missing event")

    def handle_invalid_event(self, socket: Socket):
        """Handle an invalid event"""
        self.server.send(socket, "error", "Invalid event")

    def handle(self):
        """Handle a connection"""
        server: EventServer = self.server
        socket: Socket = self.request

        address, port = socket.getpeername()
        socket_name = f"{address}:{port}"

        server.sockets[socket_name] = socket

        for handler in server.connect_handlers:
            handler(socket_name, socket)

        while True:
            try:
                packet = Packet.receive(socket)
                if packet is None:
                    break

                event = packet.event
                message = packet.message

                server.widcard_handler(event, message, socket_name, socket)
                server.event_handlers[event](event, message, socket_name, socket)

            except ValueError:
                self.handle_missing_event(socket)
                continue
            except KeyError:
                self.handle_invalid_event(socket)
                continue
            except Exception as exception:  # pylint: disable=broad-except
                logger.exception(exception)

        for handler in server.disconnect_handlers:
            handler(socket_name, socket)

        server.sockets.pop(socket_name)
