import asyncio
from typing import List, Tuple

from uwuFileShare.shared.services.uwu_protocol.base_handler import UWUHandlerBase
from uwuFileShare.shared.services.uwu_protocol.protocol import UWUProtocol
from uwuFileShare.shared.services.uwu_protocol.enums import (
    RequestAction, ResponseAction, MessageType, EventAction
)


class Handler(UWUHandlerBase):
    def __init__(self, node: "PeerNode"):
        self.node = node
        self.pending_responses = {}

    def bind(self):
        return {
            (MessageType.REQUEST, RequestAction.REGISTER): self.on_register_request, # Register with informants
            (MessageType.REQUEST, RequestAction.GET_DHT): self.on_get_dht_request, # Get DHT from informants
        }

    async def periodical_tasks(self):
        """
        Periodical tasks used by the peer node. Tries tasks and adds a timeout to them.
        """
        print("[UWU] Periodical tasks running...")

        for informant in self.node.get_informants():
            try:
                reader, writer = await asyncio.open_connection(informant[0], informant[1])
            except Exception as e:
                print(f"[UWU] Failed to connect to {informant}: {e}")
                continue

            try:
                # Set a timeout for the register request (e.g., 3 seconds)
                await asyncio.wait_for(self.on_register_request(None, reader, writer), timeout=3.0)
            except asyncio.TimeoutError:
                print(f"[UWU] Timeout waiting for response from {writer.get_extra_info('peername')}")
            except Exception as e:
                print(f"[UWU] Error communicating with {writer.get_extra_info('peername')}: {e}")
            finally:
                writer.close()
                await writer.wait_closed()

        print("[UWU] Periodical tasks finished...")

    async def on_register_request(self, message: dict, reader, writer):
        """
        This register request, requests to all informants to register the peer files that is sending the request.
        :param message:
        :param reader:
        :param writer:
        :return:
        """
        print("[UWU] Registering files to informant.")

        try:
            files: List[Tuple[str, str]] = [(filename, "") for filename in self.node.get_shared_files()]

            if not files:
                print("[UWU] No files to register.")
                return

            msg_data = {
                "files": files
            }

            msg = UWUProtocol.create_message(
                msg_type=MessageType.REQUEST,
                action=RequestAction.REGISTER,
                peer_info={"host": self.node.host, "port": self.node.port},
                data=msg_data
            )

            writer.write(msg)
            await writer.drain()

        except asyncio.TimeoutError:
            print(f"[UWU] Timeout waiting for response from {writer.get_extra_info("peername")}")
        except Exception as e:
            print(f"[UWU] Error communicating with informant {writer.get_extra_info("peername")}: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def on_get_dht_request(self, message: dict, reader, writer):
        """
        Handles the request to get the DHT from informants.
        """
        print("[UWU] Getting DHT from informants.")

        informants: List[str, int] = self.node.get_informants()

        if not informants:
            print("[UWU] No informants to get DHT from.")
            return

        for host, port in informants:
            informant_reader, informant_writer = await asyncio.open_connection(
                host, port
            )

            if not informant_writer:
                print(f"[UWU] Failed to connect to informant: {host}:{port}")
                continue

            msg_type = MessageType.REQUEST
            msg_action = RequestAction.GET_DHT
            msg_data = {
                "files": self.node.get_shared_files()
            }

            msg = UWUProtocol.create_message(msg_type,
                                             msg_action,
                                             {"host": self.node.host, "port": self.node.port},
                                             msg_data)

            # Send the message to the informant
            informant_writer.write(msg.encode())
            await informant_writer.drain()
            print(f"[UWU] Sent DHT request to informant: {host}:{port}")
