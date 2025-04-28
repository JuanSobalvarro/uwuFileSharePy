import json
import asyncio
import threading
import logging
from typing import Tuple

from .protocol import UWUProtocol
from .enums import MessageType, RequestAction, ResponseAction
from .base_handler import UWUHandlerBase

logging.basicConfig(level=logging.INFO)


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
        logging.info("[UWU_SERVICE] Handling client connection")

        try:
            # Set a timeout for handling the client request
            timeout = 10  # Timeout in seconds
            logging.info("[UWU_SERVICE] Waiting for data from client...")
            data = await reader.read(4096)
            if not data:
                logging.warning("[UWU_SERVICE] No data received from client.")
                return

            # Parse and validate the message
            message = UWUProtocol.parse_message(data)
            if not UWUProtocol.is_valid(message):
                logging.error("[UWU_SERVICE] Invalid message received.")
                return

            logging.info(f"[UWU_SERVICE] Message received: {message}")

            print(f"[UWU_SERVICE] Loaded handlers:{self.handlers}")

            # Find the appropriate handler
            handler = self.handlers.get((message["type"], message["action"]))
            if not handler:
                logging.error(f"[UWU_SERVICE] No handler for message type: {message['type'], message['action']}")
                return

            # Execute the handler with a timeout
            await asyncio.wait_for(handler(message, reader, writer), timeout=timeout)

        except asyncio.TimeoutError:
            logging.error("[UWU_SERVICE] Request timed out")
            response = UWUProtocol.create_message(
                MessageType.RESPONSE, ResponseAction.TIMEOUT.value, {}, {"message": "Request timed out"}
            )
            writer.write(response)
            await writer.drain()

        except Exception as e:
            logging.error(f"[UWU_SERVICE] Error handling client: {e}")

        finally:
            writer.close()
            await writer.wait_closed()
            logging.info("[UWU_SERVICE] Connection closed")

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
            logging.info("[UWU_SERVICE] Starting serve forever")
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
        Runs the periodical_tasks() method every `interval` seconds in a non-blocking manner.
        """
        print(f"[UWU_SERVICE] Periodic task loop started with interval = {interval}s")
        try:
            while True:
                # Schedule the periodic task and allow other tasks to run
                await asyncio.sleep(interval)
                asyncio.create_task(self.periodical_tasks())
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
        print("[UWU_SERVICE] Starting server...")
        threading.Thread(target=self.__server_thread_func, daemon=True).start()
