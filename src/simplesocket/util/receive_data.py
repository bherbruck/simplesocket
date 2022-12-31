from socket import socket as Socket


def receive_data(socket: Socket, buffer_size: int = 1024, end="\n") -> bytes:
    response = b""
    while True:
        data = socket.recv(buffer_size)
        response += data
        if not data:
            return None
        if response.endswith(end.encode("utf-8")):
            break
    return response
