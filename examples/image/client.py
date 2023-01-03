# pylint: disable=all

from time import sleep
from simplesocket import EventClient

HOST = "localhost"
PORT = 3000


def read_file(path: str) -> bytes:
    with open(path, "rb") as file:
        return file.read()


with EventClient(HOST, PORT) as client:

    @client.on("connect")
    def connect():
        print("connected")

    @client.on("disconnect")
    def disconnect():
        print("disconnected")

    sleep(1)

    while True:
        image_data = read_file("./examples/image/input.jpg")
        # print the length of the image
        print(f"image length: {len(image_data)}")
        # send image to the server
        is_sent = client.send("image", image_data)
        if not is_sent:
            print("failed to send image")
            # break
        else:
            print("image sent")
        sleep(1)
