import socket, ssl, time
from handler import ChatHandler
from config import *

def main():
    # Create a socket
    irc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Create an SSLContext object
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)

    # Set cert_reqs to CERT_NONE to disable certificate verification
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    # Wrap the socket in an SSL/TLS context using the SSLContext object
    irc_socket = context.wrap_socket(irc_socket, server_hostname = server)

    # Connect to the server
    try:
        print(f"Connecting to {server}...")
        irc_socket.connect((server, port))
        time.sleep(1)
        print("Authenticating with /PASS method...")
        irc_socket.send(f"PASS {password}\n".encode())
        time.sleep(1)
        print(f"Setting nickname '{nickname}'...")
        irc_socket.send(f"NICK {nickname}\n".encode())
        time.sleep(1)
        irc_socket.send(f"USER {nickname} 0 * :{nickname}\n".encode())
        time.sleep(1)
        print(f"Joining channel {channel}...")
        irc_socket.send(f"JOIN {channel}\n".encode())
        time.sleep(1)
        print("Connected!\n")
    except Exception:
        print("Something went wrong!")
        return

    # Set up the handler for processing input from chat
    Bot = ChatHandler()

    # Begin process loop
    while True:
        # Receive any new message as "data"
        data = irc_socket.recv(1024).decode()

        # Filter the data
        irc_msg_cmd = data.split()[1]
        if data.startswith(f":{server} "): print(data) # Don't process server welcome messages
        elif irc_msg_cmd == "PART": continue # Ignore spammy PART messages
        elif irc_msg_cmd == "PING": irc_socket.send("PONG\n".encode()) # Prevent timeout
        elif irc_msg_cmd == "PRIVMSG":
            # Send data to handler to decide whether or not to send a reply
            print(data)
            reply = Bot.handle_input(data)
            if reply is not None:
                # Send reply
                irc_socket.send(reply.encode())
        else: print(data) # Print miscellaneous messages

if __name__ == "__main__":
    main()
