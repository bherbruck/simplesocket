class EventHandler:
    def __init__(self):
        self.event_handlers: dict[str, callable] = {}
        self.connect_handlers: dict[str, callable] = []
        self.disconnect_handlers: dict[str, callable] = []

    def on(self, event):
        def decorator(func):
            if event == "connect":
                self.connect_handlers.append(func)
            elif event == "disconnect":
                self.disconnect_handlers.append(func)
            else:
                self.event_handlers[event] = func
            return func

        return decorator
