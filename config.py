from secret_tokens import irc_token, api_token

# IRC Config
server = "irc.ripple.moe"
port = 6697
channels = ["#osu"]
default_channel = "#osu"
nickname = "hellothere"
password = irc_token

# Bot Config
command_prefix = "!"

# Database Config
db_path = "db/storage.db"

# Ripple API Config
ripple_token = api_token
ripple_base_url = "https://ripple.moe/api/v1"

# Delta API Config
delta_token = api_token
delta_base_url = "https://c.ripple.moe/api/v2"
