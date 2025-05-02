"""

Created by Taif Qureshi
Github: https://github.com/TaifQureshi

"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, filters, Application
import logging
from typing import Callable, List, Any

logger = logging.getLogger("bot")


def smart_keyboard(elements: List[Any], columns=2) -> List:
    """
    :param elements:
        list of telegram InlineKeyboardButton, or any element
    :param columns:
        no to columns to arrange the element
    :return:
        list of list containing elements
    rearranged element in specified shape or columns and row
    """
    kb = []
    ele = []
    column_count = 1

    for element in elements:
        ele.append(element)
        if column_count == columns:
            kb.append(ele)
            ele = []
            column_count = 1
        else:
            column_count = column_count + 1

    if len(ele) > 0:
        kb.append(ele)

    return kb


def add_keyboard(data: dict, columns=2) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for name, value in data.items():
        inline_keyboard.append(InlineKeyboardButton(name, callback_data=value))
    return InlineKeyboardMarkup(smart_keyboard(inline_keyboard, columns))


def get_chat_id_user_name(update: Update):
    chat_id = None
    user_name = None
    if update.message is not None:
        chat_id = update.message.chat_id
        user_name = update.message.from_user.username
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat_id
        user_name = update.callback_query.from_user.username

    return chat_id, user_name


class TelegramBot(object):
    def __init__(self, token):
        """
        :param token:
            telegram bot token
        """
        self._bot = Application.builder().token(token).build()

    def start(self):
        """
        :return:

        Function to use while using Twisted reactor
        """
        print("Bot started")
        self._bot.run_polling(allowed_updates=Update.ALL_TYPES)
        self._bot.add_error_handler(self.error)

    async def error(self,update, context) -> None:
        """

        :param update:
            telegram Update
        :param context:
            telegram context
        :return:

        logs the error while handling bot command
        """
        logger.warning('Update "%s" caused error "%s"', update, context.error)
        logger.error(context.error)

    def add_command(self, command, callback: Callable) -> None:
        """
        :param command:
            bot command
        :param callback:
            callback function to run when command is received
        :return:

        bind the telegram command to the function
        """
        self._bot.add_handler(CommandHandler(command, callback))

    def add_message_handler(self, callback: Callable) -> None:
        """
        :param callback:
            set the callback function when user enter message
        :return:
        """
        self._bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback))

    async def send_message(self, update: Update, message):
        await update.message.reply_text(message)

    async def send_markup(self, update, message, markup: InlineKeyboardMarkup):
        await update.message.reply_text(message, reply_markup=markup)

