import asyncio
import ssl

from websockets.asyncio.client import connect, ClientConnection

from .logger import Logger
from .ws_message import WebsocketMessageType, WebsocketMessage
from .score import Score

HEARTBEAT_RATE = 50
HEARTBEAT_TIMEOUT = 5


class RippleWebsocketClient:
    def __init__(self, websocket_url: str, token: str):
        self.logger = Logger(self.__class__.__name__)

        self.url = websocket_url
        self.token = token

        self.websocket: ClientConnection | None = None
        self.alive = asyncio.Event()
        self.last_scores: dict[str, Score] = {}

    async def run(self):
        await self.setup()

        handler_task = asyncio.create_task(self.handle_server(), name="Handler Task")
        heartbeat_task = asyncio.create_task(self.handle_heartbeat(), name="Heartbeat Task")

        await asyncio.gather(handler_task, heartbeat_task)

    async def connect(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        self.logger.log(f"Connecting to websocket...")

        self.websocket = await connect(self.url, ssl=context)

        self.logger.log("Connected!\n")

    async def setup(self):
        self.logger.log("Authenticating with token...")
        websocket_message = WebsocketMessage(WebsocketMessageType.IDENTIFY, data={"token": self.token, "is_bearer": False})
        await self.send(websocket_message.serialize())

        self.logger.log("Subscribing to scores...")
        websocket_message = WebsocketMessage(WebsocketMessageType.SUBSCRIBE_SCORES)
        await self.send(websocket_message.serialize())

    async def handle_server(self):
        while True:
            message = await self.recv()

            try:
                ws_message = WebsocketMessage.deserialize(message)
                await self.handle_message(ws_message)
            except KeyError:
                continue

    async def handle_heartbeat(self):
        while True:
            await self.heartbeat(HEARTBEAT_TIMEOUT)
            await asyncio.sleep(HEARTBEAT_RATE)

    async def send(self, message: str):
        await self.websocket.send(message)

    async def recv(self) -> str:
        message = await self.websocket.recv()
        return message

    async def heartbeat(self, timeout: int):
        self.alive.clear()

        ws_message = WebsocketMessage(WebsocketMessageType.PING)
        await self.send(ws_message.serialize())

        await asyncio.wait_for(self.alive.wait(), timeout)

    async def handle_message(self, ws_message: WebsocketMessage):
        match ws_message.type:
            case WebsocketMessageType.PONG:
                self.alive.set()
            case WebsocketMessageType.NEW_SCORE:
                score = Score(**ws_message.kwargs["data"])
                self.last_scores[score.username] = score
            case _:
                self.logger.log(ws_message.serialize())
