from enum import Enum


class IRCCommand(Enum):
    PRIVMSG = "PRIVMSG {0} :{1}\n"
    PASS = "PASS {0}\n"
    NICK = "NICK {0}\n"
    USER = "USER {0} 0 * :{0}\n"
    JOIN = "JOIN {0}\n"
    PART = "PART {0}\n"
    NOTICE = "NOTICE {0} :[NOTICE]: {1}\n"
    QUIT = "QUIT\n"
    PING = f"PING irc.ripple.moe\n"
    PONG = f"PONG\n"
    ERROR = f"ERROR\n"

    def compose(self, *args) -> str:
        return self.value.format(*args)
