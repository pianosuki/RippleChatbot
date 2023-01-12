import re
from .context import ContextManager

class ChatHandler:
    def __init__(self, Client, command_prefix):
        self.Client = Client
        self.command_prefix = command_prefix
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
        self.mod_names = {
            "-Easy": "EZ",
            "-NoFail": "NF",
            "-HalfTime": "HT",
            "-SpunOut": "SO",
            "+Hidden": "HD",
            "+SuddenDeath": "SD",
            "+Perfect": "PF",
            "+HardRock": "HR",
            "+DoubleTime": "DT",
            "+Nightcore": "NC",
            "+Flashlight": "FL",
            "~Relax~": "RX",
            "~Autopilot~": "AP",
            "|Autoplay|": "AT",
            "|Cinema|": "CM",
            "|1K|": "1K",
            "|2K|": "2K",
            "|3K|": "3K",
            "|4K|": "4K",
            "|5K|": "5K",
            "|6K|": "6K",
            "|7K|": "7K",
            "|8K|": "8K",
            "|9K|": "9K",
            "|10K|": "10K",
            "|12K|": "12K",
            "|14K|": "14K",
            "|16K|": "16K",
            "|18K|": "18K",
            "|20K|": "20K"
        }

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
        if ctx.message.startswith(self.command_prefix):
            ctx.type = "COMMAND"
        elif ctx.message.startswith("\x01ACTION"):
            ctx.type = "ACTION"
        else:
            ctx.type = "TEXT"

        # Pass collected context to the appropriate type of sub-handler
        match ctx.type:
            case "COMMAND":
                self.handle_command(ctx)
            case "ACTION":
                self.handle_action(ctx)
            case "TEXT":
                self.handle_text(ctx)

    def handle_command(self, ctx):
        # Parse the command and argument(s) from message
        parts = ctx.message.split()
        ctx.command = parts[0].lstrip(self.command_prefix)
        args = parts[1:]

        # Look up the function for the command and call it
        function = self.commands.get(ctx.command)
        if function:
            function(ctx, *args)
        else:
            self.Client.log(f"Invalid command: '{ctx.command}'\n")

    def handle_action(self, ctx):
        # Parse the action that the user is performing
        action_checks = {phrase: phrase in ctx.message for phrase in self.action_phrases}
        ctx.action = next((key for key in action_checks.keys() if action_checks[key]), "")

        if any(list(action_checks.values())): # TO-DO: turn this condition into "if action exists & user has auto-link enabled" (need to implement users database)
            # Turn broken /np link into beatconnect link
            self.send_beatconnect_link(ctx)
        else:
            # Handle /me message
            pass


    def handle_text(self, ctx):
        return None # Nothing here yet...

    def print_help(self, ctx, *args):
        self.Client.privmsg(f"Available commands: {', '.join([self.command_prefix + command for command in self.commands])}", channel = ctx.channel)

    def say_hello(self, ctx, *args):
        self.Client.privmsg(f"Hello there, {ctx.sender}!", channel = ctx.channel)

    def send_beatconnect_link(self, ctx):
            # Compile regex patterns
            link_pattern = re.compile(r"https://osu.(ripple.moe|ppy.sh)/beatmapsets/[0-9]+#/[0-9]+")
            beatmapset_id_pattern = re.compile(r"(?<=/)\d+(?=#)")
            beatmap_id_pattern = re.compile(r"(?<=#/)\d+(?=$)")
            song_standalone_pattern = re.compile(r".+\s-\s.+(?=\])")
            song_with_difficulty_pattern = re.compile(r".+\s-\s.+(?=\s\[(.+)\]\])")
            difficulty_pattern = re.compile(r"(?<=\[)(.+)(?=\]\])")
            mods_pattern = re.compile("|".join([re.escape(mod) for mod in self.mod_names.keys()]))

            # Check if link is found and valid
            link_match = link_pattern.search(ctx.message)
            if link_match:
                # Grab Beatmapset ID and Beatmap ID from original /np link
                np_link = link_match.group()
                ctx.beatmapset_id = int(beatmapset_id_pattern.search(np_link).group())
                ctx.beatmap_id = int(beatmap_id_pattern.search(np_link).group())

                # Find song then difficulty AND/OR mods if appropriate
                match ctx.action:
                    case x if x == self.action_phrases[0]: # Listening
                        # String guaranteed to contain neither difficulty nor mods
                        ctx.song = song_standalone_pattern.search(ctx.message[link_match.end() + 1:]).group()

                    case x if x == self.action_phrases[1] or x == self.action_phrases[3]: # Playing OR Watching
                        # String guaranteed to contain difficulty but may or may not contain mods
                        song_match = song_with_difficulty_pattern.search(ctx.message[link_match.end() + 1:])
                        ctx.song = song_match.group()
                        difficulty_match = difficulty_pattern.search(ctx.message[song_match.end():])
                        ctx.difficulty = difficulty_match.group()
                        mods_match = mods_pattern.findall(ctx.message[difficulty_match.end() + 3:])
                        if mods_match: ctx.mods = [self.mod_names[mod] for mod in mods_match]

                    case x if x == self.action_phrases[2]: # Editing
                        # String guaranteed to contain difficulty and not contain mods
                        song_match = song_with_difficulty_pattern.search(ctx.message[link_match.end() + 1:])
                        ctx.song = song_match.group()
                        difficulty_match = difficulty_pattern.search(ctx.message[song_match.end():])
                        ctx.difficulty = difficulty_match.group()

                # Compose beatconnect link using collected variables
                self.Client.privmsg(f"[Beatconnect]: [https://beatconnect.io/b/{ctx.beatmapset_id} {ctx.song}]", channel = ctx.channel)
            else:
                self.Client.log("Error finding link pattern match!?\n")
