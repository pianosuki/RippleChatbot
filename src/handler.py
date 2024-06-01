import re
from src.context import ContextManager
from src.logger import Logger

class ChatHandler():
    def __init__(self, Client, DB, Ripple, Delta, command_prefix):
        # Define the Logger
        self.logger = Logger(self.__class__.__name__)

        # IRC connection client
        self.Client = Client

        # Database manager
        self.DB = DB

        # User preferences that are stored in database and their accepted values
        self.preferences = {
            "auto_beatconnect": ["on", "off"]
        }

        # Ripple API client (v1)
        self.Ripple = Ripple

        # Ripple Delta API client (v2)
        self.Delta = Delta

        # Command prefix to listen for
        self.command_prefix = command_prefix

        # Commands to listen for
        self.commands = {
            "help": self.print_help,
            "hello": self.say_hello,
            "preferences": self.set_preferences,
            "discord": self.print_discord
        }

        # Information to print upon incomplete yet valid commands
        self.docs = {
            "help": f"Available commands: {', '.join([self.command_prefix + command for command in self.commands])}",
            "hello": "Friendly greetings between a user and their obedient bot~",
            "preferences": f"Usage: {self.command_prefix}preferences <preference_name> <value> (To list all preferences: {self.command_prefix}preferences list)",
            "discord": "Prints the Ripple Discord server invite link"
        }

        # Action phrases to listen for (/np)
        self.action_phrases = [
            "is listening to",
            "is playing",
            "is editing",
            "is watching"
        ]

        # Dictionary for translating between mods as they appear in osu!stable chat and their official abbreviations
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
        elif ctx.message.startswith(("\x01ACTION", "ACTION")):
            ctx.type = "ACTION"
        else:
            ctx.type = "TEXT"

        # Register user in database
        self.DB.add_user(self.Ripple.get_user_id(ctx.sender))

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
            self.logger.log(f"Invalid command: '{ctx.command}'")

    def handle_action(self, ctx):
        # Parse the action that the user is performing
        action_checks = {phrase: phrase in ctx.message for phrase in self.action_phrases}
        ctx.action = next((key for key in action_checks.keys() if action_checks[key]), "")

        # Check if the action is a valid /np action
        if any(list(action_checks.values())):
            # Check if the user's preferences are set to have automatic beatconnect links enabled
            if bool(self.DB.get_user_column(self.Ripple.get_user_id(ctx.sender), "auto_beatconnect")):
                # Turn broken /np link into beatconnect link
                self.send_beatconnect_link(ctx)
        else:
            # Handle /me message
            pass

    def handle_text(self, ctx):
        self.parse_for_bancho(ctx)

    def print_help(self, ctx, *args):
        # Check if user provided any arguments
        if args:
            command = args[0]
            # Check if the provided argument is another valid command
            if command in self.commands:
                # Use the provided command's doc message
                message = self.docs[command]
            else:
                message = self.docs["help"]
        else:
            # Use the this command's docs message
            message = self.docs["help"]

        # Send the message
        self.Client.privmsg(message, channel = self.get_channel(ctx))

    def say_hello(self, ctx, *args):
        # Ping, pong!
        message = f"Hello there, {ctx.sender}!"

        # Send the message
        self.Client.privmsg(message, channel = self.get_channel(ctx))

    def set_preferences(self, ctx, *args):
        # Check if user provided any arguments
        if args:
            match args[0]:
                case "list": # List preferences
                    message = f"List of preferences: {', '.join([preference for preference in self.preferences.keys()])}"
                case preference if preference in self.preferences: # User provided a valid preference
                    # Check if user provided a second argument and if that argument is valid for the provided preference
                    if len(args) > 1 and args[1] in self.preferences[preference]:
                        # Decide what message to send based on which preference and value was specified
                        # Also translate the value into what we wnat to actually store in the database
                        match preference:
                            case "auto_beatconnect":
                                match args[1]:
                                    case "on":
                                        value = 1
                                        message = "Ok, I will now automatically provide Beatconnect links for each /np you send."
                                    case "off":
                                        value = 0
                                        message = "Ok, I will no longer automatically provide Beatconnect links to you."

                        # Update the user's preference in the database
                        self.DB.update_user(self.Ripple.get_user_id(ctx.sender), preference, value)
                    else:
                        # Inform user of valid values
                        message = f"Accepted values for {preference}: {', '.join([chr(39) + value + chr(39) for value in self.preferences[preference]])}"
                case invalid: # User provided an invalid preference
                    message = f"Unknown preference: '{invalid}'"
        else:
            # Use the this command's docs message
            message = self.docs["preferences"]

        # Send the message
        self.Client.privmsg(message, channel = self.get_channel(ctx))
        
    def print_discord(self, ctx, *args):
        # Send discord link
        message = f"Ripple Discord invite link: https://discord.gg/893AKDKDwz"

        # Send the message
        self.Client.privmsg(message, channel = self.get_channel(ctx))

    def send_beatconnect_link(self, ctx):
        # Compile regex patterns
        link_pattern = re.compile(r"https://osu.(ripple.moe|ppy.sh)/beatmapsets/[0-9]+#/[0-9]+")
        beatmapset_id_pattern = re.compile(r"(?<=/)\d+(?=#)")
        beatmap_id_pattern = re.compile(r"(?<=#/)\d+(?=$)")
        song_standalone_pattern = re.compile(r".+\s-\s.+(?=\])")
        song_with_difficulty_pattern = re.compile(r".+\s-\s.+(?=\s\[(.*)\]\])")
        difficulty_pattern = re.compile(r"(?<=\[)(.*)(?=\]\])")
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
                    difficulty_match = difficulty_pattern.search(ctx.message[link_match.end() + song_match.end() + 1:])
                    ctx.difficulty = difficulty_match.group()
                    mods_match = mods_pattern.findall(ctx.message[link_match.end() + song_match.end() + difficulty_match.end() + 3:])
                    if mods_match: ctx.mods = [self.mod_names[mod] for mod in mods_match]

                case x if x == self.action_phrases[2]: # Editing
                    # String guaranteed to contain difficulty and not contain mods
                    song_match = song_with_difficulty_pattern.search(ctx.message[link_match.end() + 1:])
                    ctx.song = song_match.group()
                    difficulty_match = difficulty_pattern.search(ctx.message[link_match.end() + song_match.end() + 1:])
                    ctx.difficulty = difficulty_match.group()

            # Compose beatconnect link using collected variables and send it
            self.Client.privmsg(f"[Beatconnect]: [https://beatconnect.io/b/{ctx.beatmapset_id} {ctx.song}]", channel = self.get_channel(ctx))
        else:
            self.logger.log(f"Error finding link pattern match!?")

    def get_channel(self, ctx):
        # If it's not a private message, then use the channel the sender sent in
        # Else if it is a private message, then use the sender as the channel
        return ctx.channel if not ctx.channel == self.Client.nickname else ctx.sender

    def parse_for_bancho(self, ctx):
        if "bancho" in ctx.message:
            self.Client.privmsg(f"bancho is dead :*", channel=self.get_channel(ctx))
