from telegram.ext import Updater, InlineQueryHandler
from telegram import InlineQueryResultPhoto
import json
import logging
import itertools
from uuid import uuid4
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

updater = Updater('1213095640:AAGHYweCTVuYAWnHTxhmJLidtiG_3JX7Uu8', use_context=True)
with open('emojis.json') as f:
    emojis = json.load(f)


def getEmojiQueryResult(id, url, size):
    photo_url = f"https://static-cdn.jtvnw.net/emoticons/v1/{url}/3.0"
    thumb_url = f"https://static-cdn.jtvnw.net/emoticons/v1/{url}/1.0"
    return InlineQueryResultPhoto(id=uuid4(), photo_url=photo_url, thumb_url=thumb_url, photo_width=size[0], photo_height=size[1], description="description")
            

def callback(update, context):
    queryObject = update.inline_query
    query = queryObject.query
    queryid = queryObject.id

    if not query: 
        return

    possibleQuerysGenerator = filter(lambda x: (query.upper() in x.upper()), emojis.keys())
    possibleQuerys = list(itertools.islice(possibleQuerysGenerator, 10))
    print(possibleQuerys)
    if len(possibleQuerys) == 0:
        return

    response = list(map(lambda x: getEmojiQueryResult(emojis[x][0], emojis[x][0], emojis[x][1]), possibleQuerys))
    print(response[0].photo_url)
    print(response[0].thumb_url)
    context.bot.answer_inline_query(queryid, response, cache_time=10)
    

updater.dispatcher.add_handler(InlineQueryHandler(callback))
updater.start_polling()
updater.idle()
