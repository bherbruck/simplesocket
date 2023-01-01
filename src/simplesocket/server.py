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

    def __init__(self, *args, port=3000, **kwargs):
        # this is why I hate OOP/inheritance
        ThreadedTCPServer.__init__(
            self, ("", port), EventServerHandler, *args, **kwargs
        )
        EventHandler.__init__(self)
        self.port = port
        self.sockets: list[Socket] = []
        self.allow_reuse_address = True
        self.allow_reuse_port = True

    def send(self, socket: Socket, event: str, message: str):
        """Send an event to a socket"""
        packet = Packet.encode(event, message)
        socket.sendall(packet)

    def broadcast(self, event: str, message: str):
        """Send an event to all sockets"""
        for socket in self.sockets:
            self.send(socket, event, message)

    def close(self):
        """Close all sockets and stop the server"""
        self.shutdown()
        self.server_close()

    def start(self):
        """Start the server"""
        self.serve_forever()
        self.allow_reuse_address = True
        self.allow_reuse_port = True


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

        server.sockets.append(socket)

        for handler in server.connect_handlers:
            handler(socket)

        while True:
            try:
                packet = Packet.receive(socket)
                if packet is None:
                    break

                event = packet.event
                message = packet.message

                server.widcard_handler(socket, event, message)
                response = server.event_handlers[event](socket, event, message)
                if response is not None:
                    server.send(socket, event, response)

            except ValueError:
                self.handle_missing_event(socket)
                continue
            except KeyError:
                self.handle_invalid_event(socket)
                continue
            except Exception as exception:  # pylint: disable=broad-except
                logger.exception(exception)

        server.sockets.remove(socket)

        for handler in server.disconnect_handlers:
            handler(socket)
