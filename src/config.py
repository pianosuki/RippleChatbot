import os

from dotenv import load_dotenv

load_dotenv()

# IRC Config
host = "irc.ripple.moe"
port = 6697
default_channel = "#osu"
channels = [default_channel]
nickname = os.getenv("NICKNAME")
password = os.getenv("IRC_TOKEN")

# Bot Config
command_prefix = "!"

# Database Config
db_path = "instance/storage.db"

# Ripple API Config
ripple_token = os.getenv("API_TOKEN")
ripple_base_url = "https://ripple.moe/api/v1"

# Delta API Config
delta_token = os.getenv("API_TOKEN")
delta_base_url = "https://c.ripple.moe/api/v2"
