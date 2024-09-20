import ssl
import asyncio

from .logger import Logger
from .irc_command import IRCCommand

JOIN_TIMEOUT = 5


class IRCClient:
    def __init__(self, host: str, port: int, channels: list[str], default_channel: str, nickname: str, password: str):
        self.logger = Logger(self.__class__.__name__)

        self.host = host
        self.port = port
        self.channels = channels
        self.default_channel = default_channel
        self.nickname = nickname
        self.password = password

        self.connected = asyncio.Event()
        self.joined = asyncio.Event()
        self.alive = asyncio.Event()
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    async def _open_connection(self):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        self.reader, self.writer = await asyncio.open_connection(self.host, self.port, ssl=context)

    async def connect(self):
        self.logger.log(f"Connecting to {self.host}...")
        await self._open_connection()
        await asyncio.sleep(1)

        self.logger.log("Authenticating with /PASS method...")
        await self.auth(self.password)
        await asyncio.sleep(1)

        self.logger.log(f"Setting nickname '{self.nickname}'...")
        await self.nick(self.nickname)
        await asyncio.sleep(1)

        self.logger.log(f"Setting user '{self.nickname}'...")
        await self.user(self.nickname)
        await asyncio.sleep(1)

        self.logger.log("Connected!\n")
        self.connected.set()

    async def disconnect(self):
        self.writer.close()
        await self.writer.wait_closed()

        self.logger.log("Disconnected!\n")

    async def send(self, message: str):
        self.writer.write(message.encode())
        await self.writer.drain()

    async def recv(self) -> str:
        message = await self.reader.readline()
        return message.decode()

    async def heartbeat(self, timeout: int):
        try:
            self.alive.clear()
            await self.ping()
            await asyncio.wait_for(self.alive.wait(), timeout)

        except (ConnectionError, OSError, TimeoutError):
            raise RuntimeError(f"Connection lost!")

    async def join_channels(self):
        await self.connected.wait()
        await asyncio.sleep(1)

        self.logger.log(f"Joining channel(s): {self.channels}...")

        for channel in self.channels:
            self.joined.clear()
            await self.join(channel)
            await asyncio.wait_for(self.joined.wait(), JOIN_TIMEOUT)

    async def privmsg(self, *args, **kwargs):
        channel = kwargs["channel"] if "channel" in kwargs else self.default_channel

        for msg in args:
            message = IRCCommand.PRIVMSG.compose(channel, msg)
            self.logger.log(f":{self.nickname}!127.0.0.1 {message}")
            await self.send(message)

    async def auth(self, password: str):
        message = IRCCommand.PASS.compose(password)
        await self.send(message)

    async def nick(self, nickname: str):
        message = IRCCommand.NICK.compose(nickname)
        await self.send(message)

    async def user(self, nickname: str):
        message = IRCCommand.USER.compose(nickname)
        await self.send(message)

    async def join(self, channel: str):
        message = IRCCommand.JOIN.compose(channel)
        await self.send(message)

    async def part(self, channel: str):
        message = IRCCommand.PART.compose(channel)
        await self.send(message)

    async def notice(self, *args, **kwargs):
        channel = kwargs["channel"] if "channel" in kwargs else self.default_channel

        for msg in args:
            message = IRCCommand.NOTICE.compose(channel, msg)
            self.logger.log(f":{self.nickname}!127.0.0.1 {message}")
            await self.send(message)

    async def quit(self):
        message = IRCCommand.QUIT.compose()
        await self.send(message)

    async def ping(self):
        message = IRCCommand.PING.compose()
        await self.send(message)

    async def pong(self):
        message = IRCCommand.PONG.compose()
        await self.send(message)
