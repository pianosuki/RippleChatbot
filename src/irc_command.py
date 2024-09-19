from enum import Enum


class IRCCommand(Enum):
    PRIVMSG = "PRIVMSG {0} :{1}\r\n"
    PASS = "PASS {0}\r\n"
    NICK = "NICK {0}\r\n"
    USER = "USER {0} 0 * :{0}\r\n"
    JOIN = "JOIN {0}\r\n"
    PART = "PART {0}\r\n"
    NOTICE = "NOTICE {0} :[NOTICE]: {1}\r\n"
    QUIT = "QUIT\r\n"
    PING = f"PING irc.ripple.moe\r\n"
    PONG = f"PONG\r\n"
    ERROR = f"ERROR\r\n"

    def compose(self, *args) -> str:
        return self.value.format(*args)
