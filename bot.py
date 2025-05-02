from telegram_bot import TelegramBot, get_chat_id_user_name
from agent import graph
from langchain.schema import HumanMessage
import os
from dotenv import load_dotenv

load_dotenv(override=True)

async def message(update, context):
    chat_id, username = get_chat_id_user_name(update)
    print("Chatid ",chat_id)
    config = {"configurable": {"thread_id": str(chat_id)}}
    user_input = update.message.text
    initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "loopCheck": False  # Start with loopCheck as False
        }

    response = graph.invoke(initial_state, config)
    print(response)
    response = response["messages"][-1].content
    await bot.send_message(update, response)


if __name__ == "__main__":
    # help the set the command in telegram so user can see when / is enter
    token = os.getenv('telebram_bot')
    bot = TelegramBot(token)
    bot.add_message_handler(message)
    bot.start()
