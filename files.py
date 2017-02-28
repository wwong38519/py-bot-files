import config

import logging
import json
import math
import telegram
from telegram.ext import Updater, Filters, CallbackQueryHandler, CommandHandler, ConversationHandler, MessageHandler, Job
from telegram.chataction import ChatAction
from telegram.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.inlinekeyboardbutton import InlineKeyboardButton
import os

logger = logging.getLogger(__name__)

PROCESS = range(1)

def upload_file(bot, update, job_queue):
    logger.debug(update.message)
    chat_id = update.message.chat.id
    message_id = update.message.message_id
    file_name = update.message.document.file_name
    file_size = update.message.document.file_size
    if file_size >= config.sizeLimit:
        message = 'File {} size too big, cannot be saved.'.format(file_name)
        logger.debug(message)
        bot.sendMessage(chat_id=chat_id, reply_to_message_id=message_id, text=message)
    else:
        sizeMB = file_size/1024/1024
        job_queue.put(Job(upload_file_cb, 0, repeat=False, context=update.message))
        message = 'File Queued\nFile Name: {0}\nFile Size: {1:.2f}MB'.format(file_name, sizeMB)
        logger.debug(message)
        bot.sendMessage(chat_id=chat_id, reply_to_message_id=message_id, text=message)

def upload_file_cb(bot, job):
    logger.debug(job.context)
    chat_id = job.context.chat.id
    message_id = job.context.message_id
    file_id = job.context.document.file_id
    file_name = job.context.document.file_name
    file_size = job.context.document.file_size
    logger.debug('upload_file, file_id: {} file_name: {} file_size: {}'.format(file_id, file_name, file_size))
    file = bot.getFile(file_id)
    file.download(config.savePath + file_name)
    logger.debug('File saved to: ' + config.savePath + file_name)
    bot.sendMessage(chat_id=chat_id, reply_to_message_id=message_id, text='File {} saved!'.format(file_name))

def list_file(bot, update, user_data):
    logger.info(update)
    chat_id = update.message.chat.id
    bot.sendChatAction(chat_id=chat_id, action=ChatAction.TYPING)
    filenames = os.listdir(config.savePath)
    user_data['list'] = filenames
    if len(filenames) > config.pageLimit:
        start = 0
        buttonNext = InlineKeyboardButton('Next', callback_data=str(start+config.pageLimit))
        reply_markup = InlineKeyboardMarkup([[buttonNext]])
        message = format(filenames[start:start+config.pageLimit])
        bot.sendMessage(chat_id=chat_id, text=message, reply_markup=reply_markup)
    else:
        bot.sendMessage(chat_id=update.message.chat.id, text=format(filenames))

def list_file_cbq(bot, update, user_data):
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

def download_file_start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='Send filename to download\nSay /done when finish')
    return PROCESS

def download_file_process(bot, update):
    chat_id = update.message.chat_id
    file_names = update.message.text.split('\n')
    for file_name in file_names:
        file_path = config.savePath + file_name
        if os.path.isfile(file_path):
            bot.sendChatAction(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
            bot.sendDocument(chat_id=chat_id, document=open(file_path, 'rb'))
        else: 
            bot.sendMessage(chat_id=chat_id, text='File {} does not exist!'.format(file_name))
    return PROCESS

def download_file_done(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text='OK')
    return ConversationHandler.END

def format(list):
    return '\n'.join(list) if len(list) > 0 else 'No files'

def help(bot, update):
    message = '''Hello!
        Send me documents and they will be saved
        Say /list and I will show you what I have
        Say /download and tell me file you wish to load
        Say /done when you've got all you need
    '''
    bot.sendMessage(chat_id=update.message.chat_id, text=message)


def main():
    updater = Updater(token=config.token)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', help)
    
    upload_handler = MessageHandler(Filters.document, upload_file, pass_job_queue = True)
    
    list_handler = CommandHandler('list', list_file, pass_user_data = True)
    list_cbq_handler = CallbackQueryHandler(list_file_cbq, pass_user_data = True)
    
    download_handler = ConversationHandler(
        entry_points = [CommandHandler('download', download_file_start)],
        states = {
            PROCESS: [MessageHandler(Filters.text, download_file_process)]
        },
        fallbacks = [CommandHandler('done', download_file_done)]
    )
    
    unknown_handler = MessageHandler(Filters.all, help)

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(upload_handler)
    dispatcher.add_handler(list_handler)
    dispatcher.add_handler(list_cbq_handler)
    dispatcher.add_handler(download_handler)
    dispatcher.add_handler(unknown_handler)

    logger.info('Start running.')
    updater.start_polling()
    updater.idle()

main()
