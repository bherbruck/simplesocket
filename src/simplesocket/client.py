"""A client that can send and receive events"""

import logging
from socket import socket as Socket, AF_INET, SOCK_STREAM
import threading
from time import sleep

from event_handler import EventHandler  # pylint: disable=import-error
from packet import Packet  # pylint: disable=import-error


logger = logging.getLogger(__name__)


class EventClient(EventHandler):
    """A client that can send and receive events"""

    def __init__(self, host: str, port: int, should_reconnect: bool = True):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = Socket(AF_INET, SOCK_STREAM)
        self.receive_thread = threading.Thread(target=self._receive)
        self.receive_thread.daemon = True
        self.should_reconnect = should_reconnect

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, _, __, ___):
        self.close()

    def connect(self):
        """Connect to the server and start the receive thread"""
        try:
            self.socket.connect((self.host, self.port))
            self.receive_thread.start()
            return True
        except:  # pylint: disable=bare-except
            logger.error("Connection refused")
            if self.should_reconnect:
                sleep(1)
                logger.info("Reconnecting...")
                return self.connect()
            return False

    def _receive(self):
        for handler in self.connect_handlers:
            handler()
        while True:
            try:
                packet = Packet.receive(self.socket)
                if packet is None:
                    break

                event = packet.event
                message = packet.message

                self.widcard_handler(event, message)
                self.event_handlers[event](event, message)

            except ValueError:
                continue
            except KeyError:
                continue
            except BrokenPipeError:
                break
            except Exception as exception:  # pylint: disable=broad-except
                logger.exception(exception)
        for handler in self.disconnect_handlers:
            handler()
        if self.should_reconnect:
            self.close()
            self.connect()

    def send(self, event: str, message: str):
        """Send an event to the server"""
        packet = Packet.encode(event, message)
        self.socket.sendall(packet)

    def close(self):
        """Close the connection to the server"""
        self.socket.close()
