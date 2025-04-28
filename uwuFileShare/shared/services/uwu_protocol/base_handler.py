# services/base_handler.py

from .enums import MessageType

class UWUHandlerBase:
    """
    Declare one method per RequestAction (or group of them).
    Subclasses must override the ones they care about.
    """
    async def on_action(self, message, addr, reader, writer):
        """
        Handle the action. This is an example.
        """
        raise NotImplementedError("This is just an example")

    def bind(self):
        # return a dict of action → bound coroutine
        return {
            "action":  self.on_action,
        }
