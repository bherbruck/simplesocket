import logging
from socket import socket as Socket, AF_INET, SOCK_STREAM
import threading

from event_handler import EventHandler
from packet import Packet


logger = logging.getLogger(__name__)


class EventClient(EventHandler):
    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, _, __, ___):
        self.close()

    def connect(self):
        try:
            self.socket = Socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.host, self.port))

            self.receive_thread = threading.Thread(target=self._receive)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            return True
        except ConnectionRefusedError:
            logger.error(f"Connection to {self.host}:{self.port} refused")
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
            except Exception as e:
                logger.exception(e)
        for handler in self.disconnect_handlers:
            handler()

    def send(self, event: str, message: str):
        packet = Packet.encode(event, message)
        self.socket.sendall(packet)

    def close(self):
        self.socket.close()
