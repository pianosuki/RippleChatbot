# Ripple IRC Chatbot

Enriching the user experience on [Ripple](https://ripple.moe/) (an osu! private server) through bringing interoperability with [Beatconnect](https://beatconnect.io) and other services directly to users in-game.

## Features

- [x] Automatically send the respective beatconnect link for every /np
- [x] Personalized settings for each user (SQLite database)
- [ ] !last command to show the user's last submitted score
- [ ] Tillerino-like functionality
- [ ] "osu!dailies" and incentive system to reward player engagement
- [ ] More to come!

## Prerequisites

- Python 3.12 or higher

## Installation

1. Clone the repository: `git clone https://github.com/pianosuki/ripplechatbot.git`
2. Navigate into the directroy: `cd ripplechatbot`
3. Create a virtual env: `python -m venv .venv`
4. Activate the venv: `source .venv/bin/activate`
5. Install requirements: `pip install -r requirements.txt`

## Configuration

1. Grab your Ripple account's IRC token from [here](https://ripple.moe/irc)
2. Create a new Ripple API token [here](https://ripple.moe/dev/tokens)
3. Create a file in the root directory called `.env` to store both those tokens
   - ```
     IRC_TOKEN=your_irc_token_here
     API_TOKEN=your_api_token_here
     NICKNAME=your_ripple_username
     ```
4. Edit the file `config.py` as needed
   - (Example) adding channels to listen on and choosing a command_prefix:
   - ```
     channels = [default_channel, "#other_channel", "yet_another_channel"]
     ...
     command_prefix = "symbol_to_use_as_prefix_here"
     ```

## Running

1. `source .venv/bin/activate`
2. `python main.py`

## Contributions

All contributions are welcome!
