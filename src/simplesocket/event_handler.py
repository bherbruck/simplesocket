class EventHandler:
    """
    Events functions should always return a string.
    """

    def __init__(self):
        self.event_handlers: dict[str, callable] = {}
        self.connect_handlers: dict[str, callable] = []
        self.disconnect_handlers: dict[str, callable] = []
        self.widcard_handler: callable = lambda *args, **kwargs: None

    def on(self, event):
        def decorator(func):
            if event == "connect":
                self.connect_handlers.append(func)
            elif event == "disconnect":
                self.disconnect_handlers.append(func)
            elif event == "*":
                self.widcard_handler = func
            else:
                self.event_handlers[event] = func
            return func

        return decorator
