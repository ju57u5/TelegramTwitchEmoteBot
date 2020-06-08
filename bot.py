from telegram.ext import Updater, InlineQueryHandler, CommandHandler, PicklePersistence
from telegram.ext.filters import Filters
from telegram import InlineQueryResultPhoto, InlineQueryResultCachedSticker
import requests
import json
import logging
import itertools
import time
from io import BytesIO
from PIL import Image
from uuid import uuid4

from structures import Emote
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

CACHE_TIME = 10
bot_persistence = PicklePersistence(filename='bot_data', store_bot_data=True)
updater = Updater('1213095640:AAGHYweCTVuYAWnHTxhmJLidtiG_3JX7Uu8', persistence=bot_persistence, use_context=True)

def get_emoji_size(id):
    photo = f"https://static-cdn.jtvnw.net/emoticons/v1/{id}/3.0"
    resp = requests.get(photo, headers={'User-Agent':'Mozilla5.0(Google spider)'})
    img = Image.open(BytesIO(resp.content))
    return img.size

def get_emoji_query_result(emote_code, cached_emotes):
    selected_emote = cached_emotes[emote_code]
    file_id = selected_emote["file_id"]
    return InlineQueryResultCachedSticker(id=emote_code, sticker_file_id=file_id)

def create_or_get_emote_data(context):
    if "cached_channels" not in context.bot_data:
             context.bot_data["cached_channels"] = list()
    if "emotes" not in context.bot_data:
             context.bot_data["emotes"] = dict()

    return context.bot_data["cached_channels"], context.bot_data["emotes"]

def cache_stickers(context):
    resp_emotes = context.job.context["resp_emotes"]
    if not resp_emotes:
        context.job.schedule_removal()
        return
    emote = resp_emotes.pop()

    cached_emotes = context.bot_data["emotes"]
    chat_id = context.job.context["chat_id"]
    emote_id = emote["id"]
    emote_code = emote["code"]

    if emote_code in cached_emotes:
        return

    photo_url = f"https://www.ju57u5.de/telegrambot.php?id={emote_id}"
    message = context.bot.sendSticker(chat_id=chat_id, sticker=photo_url, disable_notification=True)
    sticker = message.sticker
    file_id = sticker.file_id

    cached_emotes[emote["code"]] = {"emote_id": emote_id, "file_id": file_id}


def add_emote_command_handler(update, context):
    try:
        channel_id = int(context.args[0])
        cached_channels, cached_emotes = create_or_get_emote_data(context)
        
        if channel_id in cached_channels:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Channel was already added to the bot but I'm gonna check if there are new emotes")
            
        
        channel_api_url = f"https://api.twitchemotes.com/api/v4/channels/{channel_id}"
        resp = requests.get(channel_api_url)
        if resp.status_code == 404:
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"Error: channel with id {channel_id} not found.")
            return
        if resp.status_code != 200:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Error: can't reach twitchemotes API.")
            return

        resp_emotes = resp.json()["emotes"]
        context.job_queue.run_repeating(cache_stickers, interval=5, context={"resp_emotes": resp_emotes, "chat_id": update.message.chat_id})        
        
        cached_channels.append(channel_id)

    except ValueError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Argument channel id must be a whole number.")
    except IndexError:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Missing argument: channel id")
         

def inline_query_handler(update, context):
    cached_channels, cached_emotes = create_or_get_emote_data(context)
    query_text = update.inline_query.query
    query_id = update.inline_query.id

    if not query_text: 
        return

    possible_queries = filter(lambda x: (query_text.upper() in x.upper()), cached_emotes.keys())
    first_results = list(itertools.islice(possible_queries, 12))

    if len(first_results) == 0:
        context.bot.answer_inline_query(query_id, [], cache_time=CACHE_TIME)
        return
    
    print(first_results)
    response = list(map(lambda emote_code: get_emoji_query_result(emote_code, cached_emotes), first_results))
    context.bot.answer_inline_query(query_id, response, cache_time=CACHE_TIME)
    

if __name__ == "__main__":
    updater.dispatcher.add_handler(InlineQueryHandler(inline_query_handler))
    updater.dispatcher.add_handler(CommandHandler('add', add_emote_command_handler, filters=Filters.regex(r"[0-9]*")))
    updater.start_polling()
    updater.idle()
