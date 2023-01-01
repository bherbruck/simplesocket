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
    +---------------+---------------+----------+----------+
    | Packet Length | Event Length  | Event    | Message  |
    | (2 bytes)     | (2 bytes)     | (utf-8)  | (utf-8)  |
    +---------------+---------------+----------+----------+
    ```
    """

    HEADER_LENGTH = 4

    def __init__(self, event: str, message: str):
        self.event = event
        self.message = message

    @staticmethod
    def encode(event: str, message: str) -> bytes:
        """Encode a event and message into a packet."""
        event_bytes = event.encode("utf-8")
        message_bytes = message.encode("utf-8")
        packet_length = len(event_bytes) + len(message_bytes) + Packet.HEADER_LENGTH
        event_length = len(event_bytes)
        return (
            struct.pack("!HH", packet_length, event_length)
            + event_bytes
            + message_bytes
        )

    @staticmethod
    def decode(packet: bytes) -> "Packet":
        """Decode a packet into a event and message."""
        packet_length, event_length = struct.unpack("!HH", packet[:4])
        event: bytes = packet[
            Packet.HEADER_LENGTH : Packet.HEADER_LENGTH + event_length
        ].decode("utf-8")
        data: bytes = packet[
            Packet.HEADER_LENGTH + event_length : packet_length + Packet.HEADER_LENGTH
        ].decode("utf-8")
        return Packet(event, data)

    @staticmethod
    def receive(socket: Socket) -> "Packet":
        """Receive a packet from a socket."""
        header = socket.recv(4)
        if not header or len(header) != Packet.HEADER_LENGTH:
            return None

        packet_length, event_length = struct.unpack("!HH", header)
        event = socket.recv(event_length)
        data = socket.recv(packet_length - event_length - Packet.HEADER_LENGTH)
        return Packet.decode(header + event + data)
