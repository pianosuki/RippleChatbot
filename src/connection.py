import socket, ssl, time
from src.logger import Logger

class SocketConnection:
    def __init__(self, server, port, channels, default_channel, nickname, password):
        # Define the Logger
        self.logger = Logger(self.__class__.__name__)

        # Store configuration parameters
        self.server = server
        self.port = port
        self.channels = channels
        self.default_channel = default_channel
        self.nickname = nickname
        self.password = password

        # Set up the socket
        self.irc_socket = self.createSocket(self.server)

    def createSocket(self, server_hostname):
        # Create a socket
        irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Create an SSLContext object
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

        # Set cert_reqs to CERT_NONE to disable certificate verification
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Wrap the socket in an SSL/TLS context using the SSLContext object
        irc_socket = context.wrap_socket(irc_socket, server_hostname = server_hostname)

        return irc_socket

    def connect(self):
        # Connect to the server
        try:
            self.logger.log(f"Connecting to {self.server}...")
            self.irc_socket.connect((self.server, self.port))
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
        except Exception as error:
            self.logger.log(f"Something went wrong! Printing error...\n{error}")

    def disconnect(self):
        pass # TO-DO: handle graceful disconnecting and reconnecting attempts

    def send(self, message):
        # Encode with UTF-8 and send IRC message to server
        self.irc_socket.send(message.encode())

    def recv(self):
        # Receive and decode a message from the server
        message = self.irc_socket.recv(1024).decode()

        return message

    def privmsg(self, *args, **kwargs):
        # Deal with any potential keyword arguments passed in
        channel = kwargs["channel"] if "channel" in kwargs else self.default_channel

        # Send each argument passed in as a separate message
        for msg in args:
            message = self.composeMessage("PRIVMSG").format(channel, msg)

            # Log the outgoing message to console
            self.logger.log(f":{self.nickname}!127.0.0.1 {message}")

            # Send the message to server
            self.send(message)

    def auth(self, password):
        message = self.composeMessage("PASS").format(password)
        self.send(message)

    def nick(self, nickname):
        message = self.composeMessage("NICK").format(nickname)
        self.send(message)

    def user(self, nickname):
        message = self.composeMessage("USER").format(nickname)
        self.send(message)

    def join(self, channel):
        message = self.composeMessage("JOIN").format(channel)
        self.send(message)

    def part(self, channel):
        message = self.composeMessage("PART").format(channel)
        self.send(message)

    def notice(self, *args, **kwargs):
        # Deal with any potential keyword arguments passed in
        channel = kwargs["channel"] if "channel" in kwargs else self.default_channel

        # Send each argument passed in as a separate message
        for msg in args:
            message = self.composeMessage("NOTICE").format(channel, msg)

            # Log the outgoing message to console
            self.logger.log(f":{self.nickname}!127.0.0.1 {message}")

            # Send the message to server
            self.send(message)

    def quit(self):
        message = self.composeMessage("QUIT")
        self.send(message)

    def ping(self):
        message = self.composeMessage("PING")
        self.send(message)

    def pong(self):
        message = self.composeMessage("PONG")
        self.send(message)

    def composeMessage(self, command):
        # Compose the message to be compatable for IRC based on the command we want
        match command:
            case "PRIVMSG":
                message = "PRIVMSG {0} :{1}\n"
            case "PASS":
                message = "PASS {0}\n"
            case "NICK":
                message = "NICK {0}\n"
            case "USER":
                message = "USER {0} 0 * :{0}\n"
            case "JOIN":
                message = "JOIN {0}\n"
            case "PART":
                message = "PART {0}\n"
            case "NOTICE":
                message = "NOTICE {0} :[NOTICE]: {1}\n"
            case "QUIT":
                message = f"QUIT\n"
            case "PING":
                message = f"PING\n"
            case "PONG":
                message = f"PONG\n"
            case _:
                message = f"ERROR\n"

        return message
