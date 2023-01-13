from src.logger import Logger
from src.connection import SocketConnection
from src.database import DatabaseManager
from src.ripple import RippleAPIClient
from src.delta import DeltaAPIClient
from src.handler import ChatHandler
from config import *

def main():
    # Define the Logger
    logger = Logger("IRC")

    # Set up the IRC client
    Client = SocketConnection(server, port, channels, default_channel, nickname, password)

    # Connect the client to the server
    Client.connect()

    # Initialize SQLite database manager
    DB = DatabaseManager(db_path)

    # Set up the Ripple API client (for the Ripple website specifically)
    Ripple = RippleAPIClient(ripple_base_url, api_token)

    # Set up the Ripple Delta API client (for Ripple's Bancho emulator)
    Delta = DeltaAPIClient(delta_base_url, api_token)

    # Set up the handler for processing input from chat
    Bot = ChatHandler(Client, DB, Ripple, Delta, command_prefix)

    # Begin process loop
    while True:
        # Receive any new message from the server
        data = Client.recv()

        if data:
            # Filter the received data
            irc_msg_cmd = data.split()[1]
            if data.startswith(f":{server} "): logger.log(data) # Don't process server welcome messages
            elif irc_msg_cmd == "PART": continue # Ignore spammy PART messages
            elif irc_msg_cmd == "PING": Client.pong() # Prevent timeout
            elif irc_msg_cmd == "PRIVMSG":
                # Send data to handler to do its magic
                logger.log(data)
                Bot.handle_input(data)
            else: logger.log(data) # Log miscellaneous messages

if __name__ == "__main__":
    main()
