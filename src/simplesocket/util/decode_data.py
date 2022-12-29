def decode_data(data: str | bytes) -> tuple[str, str]:
    if isinstance(data, bytes):
        data = data.decode("utf-8")
    event, payload = data.strip().split(" ", 1)
    return event, payload
