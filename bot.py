import config

import logging
import json
import telegram
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

updater = Updater(token=config.token)
dispatcher = updater.dispatcher

def echo(bot, update):
    logging.debug(update)
    bot.sendMessage(chat_id=update.message.chat_id, text=str(update))

command_handler = CommandHandler('start', echo)
echo_handler = MessageHandler(Filters.all, echo)

dispatcher.add_handler(command_handler)
dispatcher.add_handler(echo_handler)

updater.start_polling()
updater.idle()
