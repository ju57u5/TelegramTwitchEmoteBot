"""
TelegramTwitchEmoteBot

Share Twitch emotes with a Telegram chat through a quick inline command.
"""
import json
import logging
import itertools
import sys

import requests
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, PicklePersistence
from telegram.ext.filters import Filters
from telegram import InlineQueryResultCachedSticker

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

CACHE_TIME = 10


def get_emoji_query_result(emote_code, cached_emotes):
    """
    Gets the emote information for the emote indicated by emote_code out of cached_emotes
    and return an appropiately constructed InlineQueryResultCachedSticker.

    Returns InlineQueryResultCachedSticker(id=emote_code, sticker_file_id=file_id).
    """
    selected_emote = cached_emotes[emote_code]
    file_id = selected_emote["file_id"]
    return InlineQueryResultCachedSticker(id=emote_code, sticker_file_id=file_id)


def create_or_get_emote_data(context):
    """
    This will make sure that the list cached_channels and the dict emotes are initialised
    inside bot_data before returning them.

    These list and dict are used, to store the cached stickers.

    Returns the touple (cached_channels, emotes) from inside bot_data.
    """
    if "cached_channels" not in context.bot_data:
        context.bot_data["cached_channels"] = list()
    if "emotes" not in context.bot_data:
        context.bot_data["emotes"] = dict()

    return context.bot_data["cached_channels"], context.bot_data["emotes"]


def cache_stickers(context):
    """
    This job will cache stickers by sending them to the chat indicated by chat_id
    inside the jobs context.

    This is needed because Twitch emotes are generally not big enough
    to be included in a sticker pack. Fortunatly Telegram still allows a
    sticker-like behavior, if you send a regular webp file that contains
    transparency inside a private chat. This file can then be send as an
    inline result with the returned file_id.

    This job will therefore be scheduled to send all the stickers of a
    specific Twitch channel and record all file_ids inside the bots data-dictonary.

    The webp conversion is done with the php script telegrambot.php.

    When all stickers are send, the job will automatically schedule a
    removal from the job_queue.
    """
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
    message = context.bot.sendSticker(
        chat_id=chat_id, sticker=photo_url, disable_notification=True
    )
    sticker = message.sticker
    file_id = sticker.file_id

    cached_emotes[emote["code"]] = {"emote_id": emote_id, "file_id": file_id}


def add_emote_command_handler(update, context):
    """
    CommandHandler that adds emotes from a specific channel to the bots cache.

    Format: /add <channelid>.

    Emotes are determined with querries to the twitchemotes.com API.
    """
    try:
        channel_id = int(context.args[0])
        cached_channels, _ = create_or_get_emote_data(context)

    except ValueError:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Argument channel id must be a whole number.",
        )
    except IndexError:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Missing argument: channel id."
        )

    if channel_id in cached_channels:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Channel was already added to the bot, \
                  but I'm gonna check if there are new emotes.",
        )

    channel_api_url = f"https://api.twitchemotes.com/api/v4/channels/{channel_id}"
    resp = requests.get(channel_api_url)

    if resp.status_code == 404:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error: channel with id {channel_id} not found.",
        )
        return

    if resp.status_code != 200:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Error: can't reach twitchemotes API.",
        )
        return

    try:
        resp_emotes = resp.json()["emotes"]
    except KeyError:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Error: can't read response from twitchemotes API.",
        )
        return

    context.job_queue.run_repeating(
        cache_stickers,
        interval=5,
        context={"resp_emotes": resp_emotes, "chat_id": update.message.chat_id},
    )

    cached_channels.append(channel_id)


def inline_query_handler(update, context):
    """
    Handler for the inline queries of this bot.
    Inline Mode will be used to send the actual emotes to the Telegram chat.

    Format @bot <emoteName>
    """
    _, cached_emotes = create_or_get_emote_data(context)
    query_text = update.inline_query.query
    query_id = update.inline_query.id

    if not query_text:
        return

    possible_queries = filter(
        lambda x: (query_text.upper() in x.upper()), cached_emotes.keys()
    )
    first_results = list(itertools.islice(possible_queries, 12))

    if len(first_results) == 0:
        context.bot.answer_inline_query(query_id, [], cache_time=CACHE_TIME)
        return

    logging.debug(first_results)

    response = list(
        map(
            lambda emote_code: get_emoji_query_result(emote_code, cached_emotes),
            first_results,
        )
    )
    context.bot.answer_inline_query(query_id, response, cache_time=CACHE_TIME)


if __name__ == "__main__":
    try:
        with open("credentials.json") as config:
            key = json.load(config)["key"]
    except IOError as error:
        print(
            "Can't properly read credentials.json. Check if the file exists and is accessible."
        )
        print(error)
        sys.exit()

    except KeyError as error:
        print(
            "Can't properly read credentials.json. Check if the file is in the correct format."
        )
        print(error)
        sys.exit()

    bot_persistence = PicklePersistence(filename="bot_data", store_bot_data=True)
    updater = Updater(key, persistence=bot_persistence, use_context=True)

    updater.dispatcher.add_handler(InlineQueryHandler(inline_query_handler))
    updater.dispatcher.add_handler(
        CommandHandler(
            "add", add_emote_command_handler, filters=Filters.regex(r"[0-9]*")
        )
    )
    updater.start_polling()
    updater.idle()
