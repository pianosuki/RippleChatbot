class ContextManager():
    def __init__(self):
        # Guaranteed variables
        self.sender = ""
        self.channel = ""
        self.message = ""
        self.type = ""

        # Possible variables
        self.command = ""
        self.action = ""
        self.song = ""
        self.beatmapset_id = 0
        self.beatmap_id = 0
        self.difficulty = ""
        self.mods = []

    def print_context(self):
        # Debug function to print everything neatly
        print(f"Sender: {self.sender}")
        print(f"Channel: {self.channel}")
        print(f"Message: {repr(self.message)}")
        print(f"Type: {self.type}")
        if self.command: print(f"Command: {self.command}")
        if self.action: print(f"Action: {self.action}")
        if self.song: print(f"Song: {self.song}")
        if self.beatmapset_id > 0: print(f"Beatmapset ID: {self.beatmapset_id}")
        if self.beatmap_id > 0: print(f"Beatmap ID: {self.beatmap_id}")
        if self.difficulty: print(f"Difficulty: {self.difficulty}")
        if self.mods: print (f"Mods: +{''.join(self.mods)}")
        print("")
