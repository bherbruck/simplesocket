# pylint: disable=all

from argparse import ArgumentParser
from socket import socket as Socket
from sys import argv
from time import sleep, time

from simplesocket.client import EventClient as Client
from simplesocket.server import EventServer as Server


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
        def connect(address: str, socket: Socket):
            print(f"{address} connected")

        @server.on("disconnect")
        def disconnect(address: str, socket: Socket):
            print(f"{address} disconnected")

        @server.on("echo")
        def echo(event: str, message: str, address: str, socket: Socket):
            server.send(socket, event, message)

        @server.on("*")
        def wildcard(event: str, message: str, address: str, socket: Socket):
            print(f"{address} {event} {message}")

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
            packet = client.send("echo", str(current_time))
            if not packet:
                print(f"Tried to send {current_time} to echo but got {packet}")
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
        nargs="?",
    )
    if "client" in argv:
        parser.add_argument("host", type=str, default="localhost", nargs="?")
    parser.add_argument("port", type=int, default=3000, nargs="?")

    args = parser.parse_args()

    try:
        if args.mode == "server":
            run_server(args.port)
        elif args.mode == "client":
            run_client(args.host, args.port)
    except KeyboardInterrupt:
        print()
