import re
from context import ContextManager
from config import command_prefix, nickname

class ChatHandler:
    def __init__(self):
        self.nickname = nickname
        self.commands = {
            "help": self.print_help,
            "hello": self.say_hello
        }
        self.action_phrases = [
            "is listening to",
            "is playing",
            "is editing",
            "is watching"
        ]

    def handle_input(self, input):
        # Initialize context manager
        ctx = ContextManager()

        # Set the message sender's username
        ctx.sender = input[re.search(r":", input).end():re.search(r"\!", input).start()]

        # Set the channel the message was sent in
        ctx.channel = input[re.search(r"PRIVMSG ", input).end():re.search(r" :", input).start()]

        # Set the actual message body content itself
        ctx.message = input[re.search(r"(?<=:).*?:", input).end():].rstrip()

        # Determine the type of message
        if ctx.message.startswith(command_prefix):
            ctx.type = "COMMAND"
        elif ctx.message.startswith("\x01ACTION"):
            ctx.type = "ACTION"
        else:
            ctx.type = "TEXT"

        # Pass collected context to appropriate handler type
        match ctx.type:
            case "COMMAND":
                reply = self.handle_command(ctx)
            case "ACTION":
                reply = self.handle_action(ctx)
            case "TEXT":
                reply = self.handle_text(ctx)

        if reply is not None:
            # Log reply
            print(f":{self.nickname}!127.0.0.1 {reply}")

        return reply

    def handle_command(self, ctx):
        # Parse the command and argument(s) from message
        parts = ctx.message.split()
        ctx.command = parts[0].lstrip(command_prefix)
        args = parts[1:]

        # Look up the function for the command and call it
        function = self.commands.get(ctx.command)
        if function:
            reply = function(ctx, *args)
        else:
            print(f"Invalid command: '{ctx.command}'\n")
            reply = None

        return reply

    def handle_action(self, ctx):
        # Parse the action that the user is performing
        action_checks = {phrase: phrase in ctx.message for phrase in self.action_phrases}
        ctx.action = next((key for key in action_checks.keys() if action_checks[key]), "")

        if any(list(action_checks.values())): # TO-DO: turn this condition into "if action exists & user has auto-link enabled" (need to implement users database)
            # Turn broken /np link into beatconnect link
            reply = self.send_beatconnect_link(ctx)
        else:
            reply = None

        return reply


    def handle_text(self, ctx):
        return None # Nothing here yet...

    def print_help(self, ctx, *args):
        return f"PRIVMSG {ctx.channel} :Available commands: {', '.join(['!' + command for command in self.commands])}\n"

    def say_hello(self, ctx, *args):
        return f"PRIVMSG {ctx.channel} :Hello there, {ctx.sender}!\n"

    def send_beatconnect_link(self, ctx):
            # Compile regex patterns
            link_pattern = re.compile(r"https://osu.(ripple.moe|ppy.sh)/beatmapsets/[0-9]{1,10}#/[0-9]{1,10}")
            beatmapset_id_pattern = re.compile(r"\d+")
            beatmap_id_pattern = re.compile(r"(?:\d+#/)(\d+)")

            # Check if link is found and valid
            match = link_pattern.search(ctx.message)
            if match:
                # Set /np link, Beatmapset ID, Beatmap ID, and song string
                np_link = match.group()
                ctx.beatmapset_id = beatmapset_id_pattern.search(np_link).group()
                ctx.beatmap_id = beatmap_id_pattern.search(np_link).group()
                song = re.sub(r"(?<=\S)][\x01](?=$)", "", ctx.message[match.end():]).lstrip()
                # Compose beatconnect link using collected variables
                return f"PRIVMSG {ctx.channel} :[Beatconnect]: [https://beatconnect.io/b/{ctx.beatmapset_id} {song}]\n"
            else:
                print("Error finding link pattern match!?\n")
                return None
