import config

import logging
import json
import math
import telegram
from telegram.ext import Updater, Filters, CallbackQueryHandler, CommandHandler, MessageHandler, Job
from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def upload_document(bot, update):
    logger.debug(update.message)
    chat_id = update.message.chat.id
    file_name = update.message.document.file_name
    file_size = update.message.document.file_size
    if file_size >= config.sizeLimit:
        message = 'File {} size too big, cannot be saved.'.format(file_name)
        logger.debug(message)
        bot.sendMessage(chat_id=chat_id, text=message)
    else:
        sizeMB = math.ceil(file_size/1024/1024)
        queue.put(Job(upload_document_cb, 0, repeat=False, context=update.message))
        message = 'File Queued\nFile Name: {}\nFile Size: {}MB'.format(file_name, sizeMB)
        logger.debug(message)
        bot.sendMessage(chat_id=chat_id, text=message)

def upload_document_cb(bot, job):
    logger.debug(job.context)
    chat_id = job.context.chat.id
    file_id = job.context.document.file_id
    file_name = job.context.document.file_name
    file_size = job.context.document.file_size
    logger.debug('upload_file, file_id: {} file_name: {} file_name: {}'.format(file_id, file_name, file_size))
    file = bot.getFile(file_id)
    file.download(config.savePath + file_name)
    logger.debug('File saved to: ' + config.savePath + file_name)
    bot.sendMessage(chat_id=chat_id, text='File {} saved!'.format(file_name))

def list_files(bot, update, user_data):
    logger.info(update)
    filenames = os.listdir(config.savePath)
    user_data['list'] = filenames
    if len(filenames) > config.pageLimit:
        start = 0
        buttonNext = InlineKeyboardButton('Next', callback_data=str(start+config.pageLimit))
        reply_markup = InlineKeyboardMarkup([[buttonNext]])
        message = format(filenames[start:start+config.pageLimit])
        bot.sendMessage(chat_id=update.message.chat.id, text=message, reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id=update.message.chat.id, text=format(filenames))

def list_files_cbq(bot, update, user_data):
    logger.info(update)
    logger.info(user_data)
    if user_data:
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
        filenames = user_data['list']
        start = int(update.callback_query.data) if int(update.callback_query.data) > 0 else 0
        buttonPrev = InlineKeyboardButton('Previous', callback_data=str(start-config.pageLimit))
        buttonNext = InlineKeyboardButton('Next', callback_data=str(start+config.pageLimit))
        if start == 0:
            reply_markup = InlineKeyboardMarkup([[buttonNext]])
            message = format(filenames[start:start+config.pageLimit])
        elif start+config.pageLimit >= len(filenames):
            reply_markup = InlineKeyboardMarkup([[buttonPrev]])
            message = format(filenames[start:])
        else:
            reply_markup = InlineKeyboardMarkup([[buttonPrev, buttonNext]])
            message = format(filenames[start:start+config.pageLimit])
        bot.editMessageText(chat_id=chat_id, message_id=message_id, text=message, reply_markup=reply_markup)

def format(list):
    return '\n'.join(list) if len(list) > 0 else 'No files'

def start(bot, update):
    logger.debug('start')
    bot.sendMessage(chat_id=update.message.chat_id, text="I'm a bot, please talk to me!")

def unknown(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Sorry, I didn't understand that command.")

def main():
    updater = Updater(token=config.token)
    dispatcher = updater.dispatcher
    queue = updater.job_queue

    start_handler = CommandHandler('start', start)
    upload_doc_handler = MessageHandler(Filters.document, upload_document)
    list_handler = CommandHandler('list', list_files, pass_user_data = True)
    list_cbq_handler = CallbackQueryHandler(list_files_cbq, pass_user_data = True)
    unknown_handler = MessageHandler(Filters.command, unknown)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(upload_doc_handler)
    dispatcher.add_handler(list_handler)
    dispatcher.add_handler(list_cbq_handler)
    dispatcher.add_handler(unknown_handler)

    updater.start_polling()
    updater.idle()
    logger.info('Running.')

main()