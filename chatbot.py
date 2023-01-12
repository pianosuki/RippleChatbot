from src.handler import ChatHandler
from src.connection import SocketConnection
from config import *

def main():
    # Set up the IRC client
    Client = SocketConnection(server, port, channels, default_channel, nickname, password)

    # Connect the client to the server
    Client.connect()

    # Set up the handler for processing input from chat
    Bot = ChatHandler(Client, command_prefix)

    # Begin process loop
    while True:
        # Receive any new message from the server
        data = Client.recv()

        if data:
            # Filter the received data
            irc_msg_cmd = data.split()[1]
            if data.startswith(f":{server} "): Client.log(data) # Don't process server welcome messages
            elif irc_msg_cmd == "PART": continue # Ignore spammy PART messages
            elif irc_msg_cmd == "PING": Client.pong() # Prevent timeout
            elif irc_msg_cmd == "PRIVMSG":
                # Send data to handler to do its magic
                Client.log(data)
                Bot.handle_input(data)
            else: Client.log(data) # Print miscellaneous messages

if __name__ == "__main__":
    main()
