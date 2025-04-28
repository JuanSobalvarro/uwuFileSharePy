import threading
import asyncio
import json
import os
import socket
import logging
from services.uwu_protocol.service import UWUService
from services.uwu_protocol.protocol import UWUProtocol
from services.uwu_protocol.base_handler import UWUHandlerBase
from services.uwu_protocol.enums import MessageType, RequestAction, ResponseAction

logging.basicConfig(level=logging.INFO)


class PeerNodeHandler(UWUHandlerBase):
    def __init__(self, peer_node):
        self.peer_node = peer_node

    def bind(self):
        """
        Bind actions to handler methods.
        """
        return {
            (MessageType.REQUEST, RequestAction.FILE_DOWNLOAD): self.handle_file_download,
            (MessageType.RESPONSE, ResponseAction.GET_DHT_RESPONSE): self.handle_get_dht_response,
            (MessageType.ERROR, True): self.handle_error,
        }

    async def handle_error(self, message, reader, writer):
        """
        Handle error messages from the informant node.
        """
        error_message = message.get("data", {}).get("message", "Unknown error")
        logging.error(f"Error from Informant Node: {error_message}")
        writer.close()
        await writer.wait_closed()

    async def handle_file_download(self, message, reader, writer):
        """
        Handle file download requests from other peers (server-side).
        """
        filename = message["data"].get("filename")
        file_path = os.path.join(self.peer_node.shared_dir, filename)

        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as file:
                    file_content = file.read()
                response = UWUProtocol.create_message(
                    msg_type=MessageType.RESPONSE,
                    action=ResponseAction.FILE_DOWNLOAD_RESPONSE.value,
                    peer_info={"host": self.peer_node.host, "port": self.peer_node.port},
                    data={"filename": filename, "content": file_content.decode("latin1")}
                )
                writer.write(response)
                await writer.drain()
                logging.info(f"Served file '{filename}' to client.")
            except Exception as e:
                logging.error(f"Error serving file '{filename}': {e}")
                writer.write(b"ERROR: Unable to read file")
                await writer.drain()
        else:
            writer.write(b"ERROR: File not found")
            await writer.drain()

    async def download_file(self, filename, host, port, save_path):
        """
        Download a file from another peer (client-side).
        """
        try:
            # Create the request message
            message = UWUProtocol.create_message(
                msg_type=MessageType.REQUEST,
                action=RequestAction.FILE_DOWNLOAD.value,
                peer_info={"host": self.peer_node.host, "port": self.peer_node.port},
                data={"filename": filename}
            )

            # Establish connection to the peer
            reader, writer = await asyncio.open_connection(host, port)

            # Send the request
            writer.write(message)
            await writer.drain()

            # Receive the response
            response_data = await reader.read()
            response = UWUProtocol.parse_message(response_data)

            if response["action"] == ResponseAction.FILE_DOWNLOAD_RESPONSE.value:
                # Save the file content
                with open(save_path, "wb") as file:
                    file.write(response["data"]["content"].encode("latin1"))
                logging.info(f"File '{filename}' downloaded successfully to '{save_path}'.")
            else:
                logging.error(f"Failed to download file: {response.get('message', 'Unknown error')}")

        except Exception as e:
            logging.error(f"Error downloading file '{filename}' from {host}:{port}: {e}")

        finally:
            if 'writer' in locals():
                writer.close()
                await writer.wait_closed()

    async def register_with_informant(self):
        """
        Send a register request to the informant node with the list of files in the shared directory.
        """
        try:
            logging.info(
                f"Registering with Informant Node at {self.peer_node.informant_host}:{self.peer_node.informant_port}")

            # Gather files in the shared directory
            files = [
                {"filename": filename, "size": os.path.getsize(os.path.join(self.peer_node.shared_dir, filename))}
                for filename in os.listdir(self.peer_node.shared_dir)
                if os.path.isfile(os.path.join(self.peer_node.shared_dir, filename))
            ]

            # Create the message using UWUProtocol
            message = UWUProtocol.create_message(
                msg_type=MessageType.REQUEST,
                action=RequestAction.REGISTER,
                peer_info={"host": self.peer_node.host, "port": self.peer_node.port},
                data={"files": files}
            )

            # Log the message for debugging
            logging.info(f"Message being sent: {message.decode()}")

            # Establish an asyncio connection
            reader, writer = await asyncio.open_connection(self.peer_node.informant_host, self.peer_node.informant_port)

            # Send the message
            writer.write(message)
            await writer.drain()

        except Exception as e:
            logging.error(f"Failed to register with Informant Node: {e}")

        finally:
            # Ensure the connection is properly closed
            if 'writer' in locals():
                writer.close()
                await writer.wait_closed()

    async def handle_dht_request(self):
        """
        Fetch the DHT from the informant node.
        """
        try:
            logging.info(f"Fetching DHT from Informant Node at {self.peer_node.informant_host}:{self.peer_node.informant_port}")

            # Create the request message
            message = UWUProtocol.create_message(
                msg_type=MessageType.REQUEST,
                action=RequestAction.GET_DHT,
                peer_info={"host": self.peer_node.host, "port": self.peer_node.port},
                data={}
            )

            # Establish connection to the informant node
            reader, writer = await asyncio.open_connection(self.peer_node.informant_host, self.peer_node.informant_port)

            # Send the request
            writer.write(message)
            await writer.drain()

        except Exception as e:
            logging.error(f"Error fetching DHT from Informant Node: {e}")


    async def handle_get_dht_response(self, message, reader, writer):
        """
        Handle the DHT response from the informant node.
        """
        logging.info("[PEER_NODE_HANDLER] Handling DHT response from Informant Node")
        try:
            logging.info("[PEER_NODE_HANDLER] Handling DHT response from Informant Node: ", message)
            dht_data = message.get("data", {})
            if dht_data:
                self.peer_node.dht = dht_data
                logging.info("DHT successfully updated from Informant Node.")
            else:
                logging.warning("Received empty DHT data from Informant Node.")
        except Exception as e:
            logging.error(f"Error processing DHT response: {e}")

    async def periodical(self):
        """
        Periodically register with the informant node and fetch the DHT.
        """
        await self.register_with_informant()
        await self.handle_dht_request()
        print(f"Periodic tasks executed. New DHT: {self.peer_node.dht}")


class PeerNode:
    def __init__(self, host="127.0.0.1", port=6001, informant_host="127.0.0.1", informant_port=6000, shared_dir=None):
        self.host = host
        self.port = port
        self.informant_host = informant_host
        self.informant_port = informant_port
        self.shared_dir = shared_dir or os.path.join(os.getcwd(), "shared")
        self.dht = {}

        # Ensure the shared directory exists
        os.makedirs(self.shared_dir, exist_ok=True)

        # Initialize UWUService with periodic registration
        self.handler = PeerNodeHandler(self)

    def download_file(self, filename, host, port, save_path):
        """
        Download a file from another peer.
        """
        asyncio.run(self.handler.download_file(filename, host, port, save_path))

    def start_peer_node(self):
        """
        Start the UWUService in a separate thread.
        """
        service = UWUService(
            host=self.host,
            port=self.port,
            handler=self.handler,
            periodical_tasks_cbk=(lambda: self.handler.periodical(), 5),
        )
        service.start_service()
