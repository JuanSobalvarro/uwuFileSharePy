from uwuFileShare.shared.services.uwu_protocol.base_handler import UWUHandlerBase
from uwuFileShare.shared.services.uwu_protocol.protocol import UWUProtocol
from uwuFileShare.shared.services.uwu_protocol.enums import (
    RequestAction, ResponseAction, MessageType
)


class Handler(UWUHandlerBase):
    def __init__(self, node: "InformantNode"):
        self.node = node

    def bind(self):
        return {
            (MessageType.REQUEST, ResponseAction.REGISTER): self.on_register_request,
            (MessageType.REQUEST, ResponseAction.GET_DHT): self.on_get_dht_request,
        }

    async def on_register_request(self, message: dict, reader, writer):
        """
        This method handles a CLIENT REQUEST for register, and sends a response back to the client. Register is an action
        that is used to register a new peer in the informant node, the peer sends all the files available by itself and the
        informant node stores that information in its DHT.
        :param message:
        :param reader:
        :param writer:
        :return:
        """
        print("[UWU_HANDLER] Register response request received.")
        data = message.get("data")

        if not data:
            print("[UWU_HANDLER] Invalid register request.")
            response = UWUProtocol.create_message(
                MessageType.RESPONSE,
                ResponseAction.REGISTER,
                {"host": self.node.host, "port": self.node.port},
                {"message": "Invalid register request."}
            )
            writer.write(response)
            await writer.drain()
            return

        # Extract the host and port from the message
        host, port = message.get("peer_info", {}).get("host"), message.get("peer_info", {}).get("port")

        files = data.get("files", [])

        if not files:
            print("[UWU_HANDLER] Invalid register request.")
            response = UWUProtocol.create_message(
                MessageType.RESPONSE,
                ResponseAction.REGISTER,
                {"host": self.node.host, "port": self.node.port},
                {"message": "The peer node does not have any file to share."}
            )
            writer.write(response)
            await writer.drain()
            return

        # Register the peer and its files in the DHT
        print("[UWU_HANDLER] Calling update node files")
        self.node.dht.update_node_files(files, host, port)

        response = UWUProtocol.create_message(
            MessageType.RESPONSE,
            ResponseAction.REGISTER,
            {"host": self.node.host, "port": self.node.port},
            {"message": "Peer registered successfully."}
        )

        print("[UWU_HANDLER] New dht:", self.node.dht.get_all_files())

        writer.write(response)
        await writer.drain()

    async def on_get_dht_request(self, message: dict, reader, writer):
        """
        THis method handles a CLIENT REQUEST and sends a response back to the client.
        :param message:
        :param reader:
        :param writer:
        :return:
        """

        dht = self.node.dht.get_all_files()

        response = UWUProtocol.create_message(
            MessageType.RESPONSE,
            ResponseAction.GET_DHT,
            {"host": self.node.host, "port": self.node.port},
            {"dht": dht}
        )

        writer.write(response)
        await writer.drain()

