# Ripple IRC Chatbot

Enriching the user experience on [Ripple](https://ripple.moe/) (an osu! private server) through bringing interoperability with [Beatconnect](https://beatconnect.io) and other services directly to users in-game.

## Features

- [x] Automatically send the respective beatconnect link for every /np
- [x] Personalized settings for each user (SQLite database)
- [ ] "osu!dailies" and incentive system to reward player engagement
- [ ] More to come!

## Prerequisites

- Python 3.10 or higher

## Installation

1. Clone the repository: `git clone https://github.com/pianosuki/ripplechatbot.git`

## Configuration

1. Grab your Ripple account's IRC token from [here](https://ripple.moe/irc)
2. Create a new Ripple API token [here](https://ripple.moe/dev/tokens)
3. Create a file in the root directory called `secret_tokens.py` to store both those tokens
   - ```
     irc_token = "your_irc_token_here"
     api_token = "your_api_token_here"
     ```
4. Edit the file `config.py` as needed
   - (Example) adding channels to listen on, setting nickname, and choosing a command_prefix:
   - ```
     channels = ["#osu", "#other_channel", "yet_another_channel", "etc."]
     ...
     nickname = "your_ripple_username_here"
     ...
     command_prefix = "symbol_to_use_as_prefix_here"
     ```

## Running

1. `python chatbot.py`

## Contributions

All contributions are welcome!
