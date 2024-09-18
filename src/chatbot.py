import re

from .connection import SocketConnection
from .context import ContextManager
from .database import DatabaseManager
from .ripple import RippleAPIClient
from .delta import DeltaAPIClient
from .logger import Logger
from .preference import Preference
from .command import Command
from .action_phrase import ActionPhrase
from .irc_command import IRCCommand
from .config import *


mod_names = {
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


class ChatBot:
    def __init__(self):
        self.logger = Logger(self.__class__.__name__)
        self.client = SocketConnection(host, port, channels, default_channel, nickname, password)
        self.db = DatabaseManager(db_path)
        self.ripple = RippleAPIClient(ripple_base_url, ripple_token)
        self.delta = DeltaAPIClient(delta_base_url, delta_token)
        self.command_prefix = command_prefix

        self.docs = {
            "help": f"Available commands: {", ".join([self.command_prefix + command.lower() for command in Command.__members__.keys()])}",
            "hello": "Friendly greetings between a user and their obedient bot~",
            "preferences": f"Usage: {self.command_prefix}preferences <preference_name> <value> (To list all preferences: {self.command_prefix}preferences list)",
            "discord": "Prints the Ripple Discord server invite link"
        }

    def run(self):
        self.client.connect()

        while True:
            message = self.client.recv()

            if not message:
                if not self.client.is_socket_alive():
                    raise RuntimeError("Connection lost")

                continue

            try:
                irc_command = IRCCommand[message.split()[1]]

            except KeyError:
                if bool(re.search(r"^\d{3}$", message.split()[1])):
                    irc_command = None
                else:
                    self.logger.log(f"Unknown IRC command: {message}")
                    continue

            match irc_command:
                case IRCCommand.PART | IRCCommand.PONG:
                    continue
                case IRCCommand.PING:
                    self.client.pong()
                case IRCCommand.PRIVMSG:
                    self.logger.log(message)
                    self.handle_message(message)
                case _:
                    self.logger.log(message)

    def handle_message(self, message: str):
        ctx = ContextManager()
        ctx.sender = message[re.search(r":", message).end():re.search(r"!", message).start()]
        ctx.channel = message[re.search(r"PRIVMSG ", message).end():re.search(r" :", message).start()]
        ctx.message = message[re.search(r"(?<=:).*?:", message).end():].rstrip()

        if ctx.message.startswith(self.command_prefix):
            ctx.type = "COMMAND"
        elif ctx.message.startswith(("\x01ACTION", "ACTION")):
            ctx.type = "ACTION"
        else:
            ctx.type = "TEXT"

        self.db.add_user(self.ripple.get_user_id(ctx.sender))

        match ctx.type:
            case "COMMAND":
                self.handle_command(ctx)
            case "ACTION":
                self.handle_action(ctx)
            case "TEXT":
                self.handle_text(ctx)

    def handle_command(self, ctx: ContextManager):
        parts = ctx.message.split()
        command_name = parts[0].lstrip(self.command_prefix).lower()
        args = parts[1:]

        try:
            ctx.command = Command[command_name.upper()]

        except KeyError:
            self.logger.log(f"Invalid command: '{command_name}'")
            return

        func = getattr(self, command_name)
        func(ctx, *args)

    def handle_action(self, ctx: ContextManager):
        action_checks = {action_phrase: action_phrase.value in ctx.message for action_phrase in ActionPhrase}

        try:
            ctx.action = next((action_phrase for action_phrase in action_checks.keys() if action_checks[action_phrase]))

        except StopIteration:
            self.logger.log("Failed to parse action")
            return

        if any(list(action_checks.values())):
            if bool(self.db.get_user_column(self.ripple.get_user_id(ctx.sender), "auto_beatconnect")):
                self.send_beatconnect_link(ctx)

    def handle_text(self, ctx: ContextManager):
        self.parse_for_bancho(ctx)

    def help(self, ctx: ContextManager, *args):
        message = self.docs["help"]

        if args:
            command = args[0]

            if command.upper() in Command.__members__:
                message = self.docs[command]

        self.client.privmsg(message, channel=self.get_channel(ctx))

    def hello(self, ctx: ContextManager):
        message = f"Hello there, {ctx.sender}!"

        self.client.privmsg(message, channel=self.get_channel(ctx))

    def preferences(self, ctx: ContextManager, *args):
        if args:
            match args[0]:
                case "list":
                    message = f"List of preferences: {", ".join([preference.lower() for preference in Preference.__members__.keys()])}"
                case preference_name if preference_name.upper() in Preference.__members__:
                    preference = Preference[preference_name.upper()]
                    message = None

                    if len(args) > 1 and args[1] in preference.value:
                        value = None

                        match preference:
                            case Preference.AUTO_BEATCONNECT:
                                match args[1]:
                                    case "on":
                                        value = 1
                                        message = "Ok, I will now automatically provide Beatconnect links for each /np you send."
                                    case "off":
                                        value = 0
                                        message = "Ok, I will no longer automatically provide Beatconnect links to you."

                        self.db.update_user(self.ripple.get_user_id(ctx.sender), preference_name, value)
                    else:
                        message = f"Accepted values for {preference}: {", ".join([chr(39) + value + chr(39) for value in preference.value])}"
                case invalid:
                    message = f"Unknown preference: '{invalid}'"
        else:
            message = self.docs["preferences"]

        self.client.privmsg(message, channel=self.get_channel(ctx))
        
    def discord(self, ctx: ContextManager):
        message = f"Ripple Discord invite link: https://discord.gg/893AKDKDwz"

        self.client.privmsg(message, channel=self.get_channel(ctx))

    def send_beatconnect_link(self, ctx: ContextManager):
        link_pattern = re.compile(r"https://osu.(ripple.moe|ppy.sh)/beatmapsets/[0-9]+#/[0-9]+")
        beatmapset_id_pattern = re.compile(r"(?<=/)\d+(?=#)")
        beatmap_id_pattern = re.compile(r"(?<=#/)\d+(?=$)")
        song_standalone_pattern = re.compile(r".+\s-\s.+(?=])")
        song_with_difficulty_pattern = re.compile(r".+\s-\s.+(?=\s\[(.*)]])")
        difficulty_pattern = re.compile(r"(?<=\[)(.*)(?=]])")
        mods_pattern = re.compile("|".join([re.escape(mod) for mod in mod_names.keys()]))

        link_match = link_pattern.search(ctx.message)

        if link_match:
            np_link = link_match.group()
            ctx.beatmapset_id = int(beatmapset_id_pattern.search(np_link).group())
            ctx.beatmap_id = int(beatmap_id_pattern.search(np_link).group())

            match ctx.action:
                case ActionPhrase.LISTENING:
                    ctx.song = song_standalone_pattern.search(ctx.message[link_match.end() + 1:]).group()
                case ActionPhrase.PLAYING | ActionPhrase.WATCHING:
                    song_match = song_with_difficulty_pattern.search(ctx.message[link_match.end() + 1:])
                    difficulty_match = difficulty_pattern.search(ctx.message[link_match.end() + song_match.end() + 1:])
                    mods_match = mods_pattern.findall(ctx.message[link_match.end() + song_match.end() + difficulty_match.end() + 3:])

                    ctx.song = song_match.group()
                    ctx.difficulty = difficulty_match.group()

                    if mods_match:
                        ctx.mods = [mod_names[mod] for mod in mods_match]
                case ActionPhrase.EDITING:
                    song_match = song_with_difficulty_pattern.search(ctx.message[link_match.end() + 1:])
                    difficulty_match = difficulty_pattern.search(ctx.message[link_match.end() + song_match.end() + 1:])

                    ctx.song = song_match.group()
                    ctx.difficulty = difficulty_match.group()

            self.client.privmsg(f"[Beatconnect]: [https://beatconnect.io/b/{ctx.beatmapset_id} {ctx.song}]", channel=self.get_channel(ctx))
        else:
            self.logger.log(f"Error finding link pattern match!?")

    def get_channel(self, ctx: ContextManager):
        return ctx.channel if not ctx.channel == self.client.nickname else ctx.sender

    def parse_for_bancho(self, ctx: ContextManager):
        if "bancho" in ctx.message:
            self.client.privmsg(f"bancho is dead :*", channel=self.get_channel(ctx))
