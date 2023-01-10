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
        self.beatmapset_id = 0
        self.beatmap_id = 0

    def print_context(self):
        print(f"Sender: {self.sender}, \
                Channel: {self.channel}, \
                Message: {repr(self.message)}, \
                Type: {self.type}\
                {', Command: ' + self.command if self.command else ''}\
                {', Action: ' + self.action if self.action else ''}\
                {', Beatmapset ID: ' + self.beatmapset_id if self.beatmapset_id > 0 else ''}\
                {', Beatmap ID: ' + self.beatmap_id if self.beatmap_id > 0 else ''}\n")
