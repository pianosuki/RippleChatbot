import asyncio

from src.chatbot import ChatBot


def main():
    chatbot = ChatBot()
    asyncio.run(chatbot.run())


if __name__ == "__main__":
    main()
