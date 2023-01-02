# pylint: disable=all

from argparse import ArgumentParser
from socket import socket as Socket
from sys import argv
from time import sleep, time

from client import EventClient as Client
from server import EventServer as Server


def run_server(port: int):
    print(f"starting server on port {port}...")
    from threading import Thread
    from time import sleep

    with Server(port=port) as server:

        def ping():
            while True:
                server.broadcast("ping", "")
                sleep(1)

        thread = Thread(target=ping)
        thread.daemon = True
        thread.start()

        @server.on("connect")
        def connect(socket: Socket):
            address, port = socket.getpeername()
            print(f"{address}:{port} connected")

        @server.on("disconnect")
        def disconnect(socket: Socket):
            address, port = socket.getpeername()
            print(f"{address}:{port} disconnected")

        @server.on("echo")
        def echo(socket: Socket, event: str, message: str):
            server.send(socket, event, message)

        @server.on("*")
        def wildcard(socket: Socket, event: str, message: str):
            address, port = socket.getpeername()
            print(f"{address}:{port} {event} {message}")

        print(f"listening on port {port}")
        server.start()


def run_client(host: str, port: int):
    print(f"connecting to {host}:{port}...")
    with Client(host, port) as client:

        @client.on("connect")
        def connect():
            print("connected")

        @client.on("disconnect")
        def disconnect():
            print("disconnected")

        @client.on("echo")
        def echo(event: str, message: str):
            print(message)

        @client.on("ping")
        def ping(event: str, message: str):
            client.send("pong", "")

        while True:
            current_time = int(time() * 1000)
            client.send("echo", str(current_time))
            sleep(0.01)
            # try:
            #     event, message = input().split(" ", 1)
            #     client.send(event, message)
            # except ValueError:
            #     print("invalid input")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "mode",
        type=str,
        help="client or server",
        choices=("client", "server"),
        default="server",
    )
    if "client" in argv:
        parser.add_argument("host", type=str)
    parser.add_argument("port", type=int)

    args = parser.parse_args()

    try:
        if args.mode == "server":
            run_server(args.port)
        elif args.mode == "client":
            run_client(args.host, args.port)
    except KeyboardInterrupt:
        print()
