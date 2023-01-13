from src.logger import Logger

class ContextManager:
    def __init__(self):
        # Define the Logger
        self.logger = Logger(self.__class__.__name__)

        # Define guaranteed variables
        self.sender = ""
        self.channel = ""
        self.message = ""
        self.type = ""

        # Define possible variables
        self.command = ""
        self.action = ""
        self.song = ""
        self.beatmapset_id = 0
        self.beatmap_id = 0
        self.difficulty = ""
        self.mods = []

    def print_context(self):
        # Debug function to print everything neatly in a block

        # Begin the block
        message_block = ["\n-----BEGIN CONTEXT BLOCK-----"]

        # Add guaranteed context to the block
        message_block.extend([
            f"\tSender: {self.sender}",
            f"\tChannel: {self.channel}",
            f"\tMessage: {repr(self.message)}",
            f"\tType: {self.type}"
        ])

        # Add possible context to the block if exists
        if self.command: message_block.append(f"\tCommand: {self.command}")
        if self.action: message_block.append(f"\tAction: {self.action}")
        if self.song: message_block.append(f"\tSong: {self.song}")
        if self.beatmapset_id > 0: message_block.append(f"\tBeatmapset ID: {self.beatmapset_id}")
        if self.beatmap_id > 0: message_block.append(f"\tBeatmap ID: {self.beatmap_id}")
        if self.difficulty: message_block.append(f"\tDifficulty: {self.difficulty}")
        if self.mods: message_block.append (f"\tMods: +{''.join(self.mods)}")

        # End the block
        message_block.append("-----END CONTEXT BLOCK-----")

        # Send the block to Logger
        self.logger.log("Printing context..." + "\n".join(message_block))
