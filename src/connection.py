import socket
import ssl
import time

from .logger import Logger
from .irc_command import IRCCommand


class SocketConnection:
    def __init__(self, host: str, port: int, channels: list[str], default_channel: str, nickname: str, password: str):
        self.logger = Logger(self.__class__.__name__)

        self.host = host
        self.port = port
        self.channels = channels
        self.default_channel = default_channel
        self.nickname = nickname
        self.password = password

        self.irc_socket = self._create_socket()

    def _create_socket(self):
        irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        irc_socket = context.wrap_socket(irc_socket, server_hostname=self.host)
        irc_socket.settimeout(10)
        irc_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        irc_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
        irc_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
        irc_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)

        return irc_socket

    def connect(self):
        self.logger.log(f"Connecting to {self.host}...")
        self.irc_socket.connect((self.host, self.port))
        time.sleep(1)

        self.logger.log("Authenticating with /PASS method...")
        self.auth(self.password)
        time.sleep(1)

        self.logger.log(f"Setting nickname '{self.nickname}'...")
        self.nick(self.nickname)
        time.sleep(1)

        self.logger.log(f"Setting user '{self.nickname}'...")
        self.user(self.nickname)
        time.sleep(1)

        self.logger.log(f"Joining channel(s): {self.channels}...")
        for channel in self.channels:
            self.join(channel)
            time.sleep(1)

        self.logger.log("Connected!\n")

    def disconnect(self):
        self.irc_socket.close()
        self.logger.log("Disconnected!\n")

    def send(self, message: str):
        self.irc_socket.send(message.encode())

    def recv(self) -> str | None:
        try:
            message = self.irc_socket.recv(1024).decode()
            return message

        except socket.timeout:
            return None

    def is_socket_alive(self) -> bool:
        try:
            self.irc_socket.send(b"")
            return True

        except (socket.error, ssl.SSLError):
            return False

    def privmsg(self, *args, **kwargs):
        channel = kwargs["channel"] if "channel" in kwargs else self.default_channel

        for msg in args:
            message = IRCCommand.PRIVMSG.compose(channel, msg)
            self.logger.log(f":{self.nickname}!127.0.0.1 {message}")
            self.send(message)

    def auth(self, password: str):
        message = IRCCommand.PASS.compose(password)
        self.send(message)

    def nick(self, nickname: str):
        message = IRCCommand.NICK.compose(nickname)
        self.send(message)

    def user(self, nickname: str):
        message = IRCCommand.USER.compose(nickname)
        self.send(message)

    def join(self, channel: str):
        message = IRCCommand.JOIN.compose(channel)
        self.send(message)

    def part(self, channel: str):
        message = IRCCommand.PART.compose(channel)
        self.send(message)

    def notice(self, *args, **kwargs):
        channel = kwargs["channel"] if "channel" in kwargs else self.default_channel

        for msg in args:
            message = IRCCommand.NOTICE.compose(channel, msg)
            self.logger.log(f":{self.nickname}!127.0.0.1 {message}")
            self.send(message)

    def quit(self):
        message = IRCCommand.QUIT.compose()
        self.send(message)

    def ping(self):
        message = IRCCommand.PING.compose()
        self.send(message)

    def pong(self):
        message = IRCCommand.PONG.compose()
        self.send(message)
