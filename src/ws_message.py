import json
from enum import Enum


class WebsocketMessageType(Enum):
    CONNECTED = {"type": "connected"}
    IDENTIFY = {"type": "identify", "data": {}}
    IDENTIFIED = {"type": "identified", "data": {}}
    PING = {"type": "ping"}
    PONG = {"type": "pong"}
    SUBSCRIBE_SCORES = {"type": "subscribe_scores", "data": []}
    SUBSCRIBED_TO_SCORES = {"type": "subscribed_to_scores", "data": []}
    NEW_SCORE = {"type": "new_score", "data": {}}

    def compose(self, **kwargs) -> str:
        return json.dumps({
            **self.value,
            **{key: value for key, value in kwargs.items() if key in self.value}
        })


class WebsocketMessage:
    def __init__(self, message_type: WebsocketMessageType, **kwargs):
        self.type = message_type
        self.kwargs = kwargs

    def serialize(self) -> str:
        return self.type.compose(**self.kwargs)

    @classmethod
    def deserialize(cls, message: str) -> "WebsocketMessage":
        message: dict = json.loads(message)
        message_type = WebsocketMessageType[message.pop("type").upper()]

        return cls(message_type, **message)
