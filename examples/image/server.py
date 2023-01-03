# pylint: disable=all

from simplesocket import EventServer
from socket import socket as Socket

PORT = 3000


def write_file(path: str, data: bytes):
    with open(path, "wb") as file:
        file.write(data)


with EventServer(port=PORT) as server:

    @server.on("connect")
    def connect(address: str, *args, **kwargs):
        print(f"{address} connected")

    @server.on("disconnect")
    def disconnect(address: str, *args, **kwargs):
        print(f"{address} disconnected")

    @server.on("image")
    def image(event: str, message: bytes, *args, **kwargs):
        print(f"image received: {len(message)} bytes")
        write_file("output.jpg", message)

    print(f"listening on port {PORT}")
    server.start()
