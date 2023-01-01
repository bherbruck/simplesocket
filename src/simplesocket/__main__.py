from argparse import ArgumentParser
from socket import socket as Socket
from sys import argv

from client import EventClient as Client
from server import EventServer as Server


def run_server(port: int):
    from threading import Thread
    from time import sleep

    with Server(port) as server:

        def ping():
            while True:
                server.broadcast("ping", "ping")
                sleep(1)

        thread = Thread(target=ping)
        thread.daemon = True
        thread.start()

        @server.on("connect")
        def connect(socket: Socket):
            print("connected")

        @server.on("disconnect")
        def disconnect(socket: Socket):
            print("disconnected")

        @server.on("echo")
        def echo(socket: Socket, event: str, message: str):
            print(message)
            server.send(socket, event, message)

        print(f"listening on port {port}")
        server.start()


def run_client(host: str, port: int):
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

    client.connect()

        while True:
            try:
                event, message = input().split(" ", 1)
                client.send(event, message)
            except ValueError:
                print("invalid input")


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
        parser.add_argument("host", type=str, default="127.0.0.1")
    parser.add_argument("port", type=int, default=3000)

    args = parser.parse_args()

    try:
        if args.mode == "server":
            run_server(args.port)
        elif args.mode == "client":
            run_client(args.host, args.port)
    except KeyboardInterrupt:
        print()
