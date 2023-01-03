"""Packet"""

import struct
from socket import socket as Socket


# This probably doesn't need to be a class, but whatever.
class Packet:
    """
    A packet is an event with a message.\n
    The first two bytes are the length of the packet.\n
    The next two bytes are the length of the event.\n
    The rest of the packet is the event and the message.\n
    ```txt
    +------------------------------+-------------------+
    | Header                       | Payload           |
    | (8 bytes)                    |                   |
    +---------------+--------------+---------+---------+
    | Packet Length | Event Length | Event   | Message |
    | (4 bytes)     | (4 bytes)    | (utf-8) | (bytes) |
    +---------------+--------------+---------+---------+
    ```
    TODO: check integrity of packet (could be done with ssl/tls)
    TODO: packet fragmentation (if we want to send large packets)
    """

    MAX_PACKET_SIZE = 65535  # (ish?)
    HEADER_LENGTH = 8

    def __init__(self, event: str, message: bytes):
        self.event = event
        self.message = message

    @staticmethod
    def encode(event: str, message: bytes) -> bytes:
        """Encode a event and message into a packet."""
        event_bytes = event.encode("utf-8")
        try:
            message_bytes = message.encode("utf-8")  # if message is a string
        except AttributeError:
            message_bytes = message
        packet_length = len(event_bytes) + len(message_bytes) + Packet.HEADER_LENGTH
        event_length = len(event_bytes)
        header = struct.pack("!LL", packet_length, event_length)
        packet = header + event_bytes + message_bytes
        return packet

    @staticmethod
    def decode(packet: bytes) -> "Packet":
        """Decode a packet into a event and message."""
        packet_length, event_length = struct.unpack(
            "!LL", packet[: Packet.HEADER_LENGTH]
        )
        event: bytes = packet[
            Packet.HEADER_LENGTH : Packet.HEADER_LENGTH + event_length
        ].decode("utf-8")
        data: bytes = packet[
            Packet.HEADER_LENGTH + event_length : packet_length + Packet.HEADER_LENGTH
        ]
        return Packet(event, data)

    @staticmethod
    def receive(socket: Socket) -> "Packet":
        """Receive a packet from a socket."""
        try:
            header = socket.recv(Packet.HEADER_LENGTH)
            if not header or len(header) != Packet.HEADER_LENGTH:
                return None
            packet_length, event_length = struct.unpack("!LL", header)
            event = socket.recv(event_length)
            data = socket.recv(packet_length - event_length - Packet.HEADER_LENGTH)
            return Packet.decode(header + event + data)
        except (ConnectionError, OSError, ValueError) as exception:
            print(exception)
            return None

    @staticmethod
    def send(socket: Socket, event: str, message: bytes):
        """Send a packet to a socket."""
        try:
            socket.sendall(Packet.encode(event, message))
            return True
        except (ConnectionError, OSError, ValueError):
            return False
