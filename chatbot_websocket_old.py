import asyncio, websockets, json
from secret_tokens import api_token as token

async def connect():
    async with websockets.connect("wss://api.ripple.moe/api/v1/ws") as websocket:
        raw_response = await websocket.recv()
        response = json.loads(raw_response)
        if response["type"] == "connected":
            print("Connected!")
        else:
            print("Error connecting to the Ripple WebSocket server.")
            return

        await websocket.send(json.dumps({"type":"identify", "data": {"token": token, "is_bearer": False}}))
        raw_response = await websocket.recv()
        response = json.loads(raw_response)
        print(response)

if __name__ == "__main__":
    asyncio.run(connect())
