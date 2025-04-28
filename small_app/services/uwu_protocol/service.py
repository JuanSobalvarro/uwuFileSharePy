import json
import asyncio
import threading
from typing import Tuple

from .protocol import UWUProtocol
from .base_handler import UWUHandlerBase

class UWUService:
    def __init__(self, host="0.0.0.0", port=6000, handler: UWUHandlerBase = None, periodical_tasks_cbk: Tuple[callable, int] = None):
        """
        Initializes the UWUService with the given parameters.
        :param host:
        :param port:
        :param handler:
        :param periodical_tasks_cbk: A tuple containing a callback function and an interval in seconds.
        """
        if handler is None:
            raise ValueError("Handler must be provided.")

        self.host = host
        self.port = port
        self.server = None
        self.loop = None
        self.server_ready = threading.Event()
        self.handler = handler
        self.handlers = self.handler.bind()
        self.periodical_tasks = periodical_tasks_cbk[0] if periodical_tasks_cbk is not None else None
        self.periodical_interval = 0 if periodical_tasks_cbk is None else periodical_tasks_cbk[1]

    def is_running(self):
        """
        Checks if the server is running.
        :return: True if the server is running, False otherwise.
        """
        return self.server is not None and self.server.is_serving()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):

        print(f"[UWU_SERVICE] Handling client connection")

        try:
            data = await reader.read()
            if not data:
                return

            # Message is the unit of communication (so the data needs to be decoded from bytes to json)
            message = UWUProtocol.parse_message(data)

            if not UWUProtocol.is_valid(message):
                print("[UWU_SERVICE] Invalid message received")
                return

            print("[UWU_SERVICE] Message received:", message)

            handler = self.handlers.get((message["type"], message["action"]))

            if not handler:
                print(f"[UWU_SERVICE] No handler for message type: {message['type'], message['action']}")
                return

            # Once we have a handler we need to pass the message, reader and writer to it
            result = await handler(message, reader, writer)

            # Once we have a result we need to do something with it, we should pass that result upper in the app layers,
            # maybe to the node cli or gui, etc. This action is defined on the type of message we are handling. If request
            # our result should be the response from the corresponding node (peer or informant), if event do nothing, everything
            # should have been exexcuted on handler, if response we should also do nothing since we are just handling a response
            # in resume a handler will return a result for any message that is a Request type, but for others it will just return true or false

            # havent found a use yet!!!!!!!!!!!! everything just executes

        except KeyboardInterrupt:
            print("[UWU_SERVICE] Server shutting down...")
            writer.close()
            await writer.wait_closed()
            print("[UWU_SERVICE] Connection closed")
            return

        except Exception as e:
            print(f"[UWU_SERVICE] Error handling client: {e}")

    async def get_server(self):
        """
        Starts the server and returns it.
        """
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        return server

    async def __start_server(self):
        """
        Starts the server and the periodic task loop.
        """
        self.server = await self.get_server()
        self.server_ready.set()

        print(f"[UWU_SERVICE] Server running on {self.host}:{self.port}")
        print("[UWU_SERVICE] Registered functions:")
        for key in self.handlers.keys():
            print(f"  - {key}")

        # Schedule periodic task loop (customize interval)
        if self.periodical_tasks and self.periodical_interval > 0:
            print(f"[UWU_SERVICE] Periodic tasks scheduled every {self.periodical_interval} seconds.")
            periodic_task = asyncio.create_task(self.__run_periodical_tasks_loop(interval=self.periodical_interval))

        try:
            async with self.server:
                await self.server.serve_forever()
        except asyncio.CancelledError:
            print("[UWU_SERVICE] Server task cancelled.")
        except Exception as e:
            print(f"[UWU_SERVICE] Exception in server loop: {e}")
        finally:
            periodic_task.cancel()
            try:
                await periodic_task
            except asyncio.CancelledError:
                print("[UWU_SERVICE] Periodic tasks cancelled.")

    async def __shutdown_server(self):
        """
        Shuts down safely the server.
        :return:
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("[UWU_SERVICE] Server shut down.")

    def __server_thread_func(self):
        """
        Thread function to run the server loop.
        """
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_until_complete(self.__start_server())
        except Exception as e:
            print(f"[ERROR] Server loop exception: {e}")
        finally:
            self.loop.close()

    async def __run_periodical_tasks_loop(self, interval: int):
        """
        Runs the periodical_tasks() method every `interval` seconds.
        """
        print(f"[UWU_SERVICE] Periodic task loop started with interval = {interval}s")
        try:
            while True:
                await asyncio.sleep(interval)
                await self.periodical_tasks()
        except asyncio.CancelledError:
            print("[UWU_SERVICE] Periodic task loop cancelled.")


    def stop_service(self):
        """
        Shuts down the server safely.
        :return:
        """
        if self.server and self.loop:
            asyncio.run_coroutine_threadsafe(self.__shutdown_server(), self.loop)

    def start_service(self):
        """
        Starts the server in a new thread.
        :return:
        """
        threading.Thread(target=self.__server_thread_func, daemon=True).start()
