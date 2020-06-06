from telegram.ext import Updater, InlineQueryHandler
from telegram import InlineQueryResultPhoto
import json
import logging
from io import BytesIO
from PIL import Image
import requests
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def getEmojiSize(id):
    photo = f"https://static-cdn.jtvnw.net/emoticons/v1/{id}/3.0"
    RANGE = 7000
    req = requests.get(photo, headers={'User-Agent':'Mozilla5.0(Google spider)','Range':'bytes=0-{}'.format(RANGE)})
    im = Image.open(BytesIO(req.content))
    return im.size

def getEmojiQueryResult(id, url, size):
    return InlineQueryResultPhoto(id=str(id), photo_url=url, thumb_url=url, photo_width=size[0], photo_height=size[1])
            

def callback(update, context):
    queryObject = update.inline_query
    query = queryObject.query
    queryid = queryObject.id

    if not query:
        allEmojis = map(lambda emoji: getEmojiQueryResult(emoji["id"]), emojis[:25])
        context.bot.answer_inline_query(queryid, list(allEmojis))
        return

    try:
        emoji = emojis[query]
        context.bot.answer_inline_query(queryid, [getEmojiQueryResult(query, emoji[0], emoji[1])])
    except:
        pass

  

updater = Updater('1213095640:AAGHYweCTVuYAWnHTxhmJLidtiG_3JX7Uu8', use_context=True)
emojis = dict()

with open('emojis.json') as f:
    data = json.load(f)
    for emoji in data:
        print(emoji["code"], emoji["id"])
        emojis[emoji["code"]] = (emoji["id"], getEmojiSize(emoji["id"]))

print("done")
updater.dispatcher.add_handler(InlineQueryHandler(callback))
updater.start_polling()

