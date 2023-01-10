# Ripple IRC Chatbot

Enriching the user experience on [Ripple](https://ripple.moe/) (an osu! private server) through bringing interoperability with [Beatconnect](https://beatconnect.io) and other services directly to users in-game.

## Features

- [x] Automatically send the respective beatconnect link for every /np
- [ ] Personalized settings for each user
- [ ] More to come!

## Prerequisites

- Python 3.10 or higher

## Installation

1. Clone the repository: `git clone https://github.com/pianosuki/ripplechatbot.git`

## Configuration

1. Grab your Ripple account's IRC token from [here](https://ripple.moe/irc)
2. Create a file in the root directory called `secret_tokens.py` to store that token
   - ```
     irc_token = "your_irc_token_here"
     ```
2. Edit the file `config.py` as needed
   - Setting nickname:
   - ```
     nickname = "your_ripple_username_here"
     ```

## Running

1. `python chatbot.py`

## Contributions

All contributions are welcome!
