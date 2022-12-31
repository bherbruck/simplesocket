import argparse
from socket import socket as Socket
from sys import argv

from client import EventClient as Client
from server import EventServer as Server


def run_server(port: int):
    with Server(port) as server:

        @server.on("connect")
        def connect(socket: Socket):
            print("connected")

        @server.on("disconnect")
        def disconnect(socket: Socket):
            print("disconnected")

        @server.on("echo")
        def echo(socket: Socket, payload: str):
            print(payload)
            return payload

        print(f"listening on port {port}")
        server.start()


def run_client(host: str, port: int):
    from util.decode_data import decode_data

    client = Client(host, port)

    @client.on("connect")
    def connect():
        print("connected")

    @client.on("disconnect")
    def disconnect():
        print("disconnected")

    @client.on("echo")
    def echo(payload: str):
        print(payload)

    client.connect()

    while True:
        event, payload = decode_data(input().encode("utf-8"))
        client.send(event, payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
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
