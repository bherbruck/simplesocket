import logging
import socket
import threading

from event_handler import EventHandler
from util.decode_data import decode_data
from util.receive_data import receive_data


logger = logging.getLogger(__name__)


class EventClient(EventHandler):
    def __init__(self, host: str, port: int):
        super().__init__()
        self.host = host
        self.port = port

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                data = receive_data(self.socket)
                if not data:
                    break

                event, payload = decode_data(data)
                self.event_handlers[event](payload)

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

    def send(self, event: str, payload: str):
        self.socket.sendall(f"{event} {payload}".encode("utf-8").strip() + b"\n")

    def close(self):
        self.socket.close()
