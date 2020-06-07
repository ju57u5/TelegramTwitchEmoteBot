import json
import logging
import requests
from io import BytesIO
from PIL import Image
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

channels = [0, 5, 44252848]

emojis = dict()

def getEmojiSize(id):
    photo = f"https://static-cdn.jtvnw.net/emoticons/v1/{id}/3.0"
    req = requests.get(photo, headers={'User-Agent':'Mozilla5.0(Google spider)'})
    im = Image.open(BytesIO(req.content))
    return im.size


emotes = []
for channel in channels:
    url = f"https://api.twitchemotes.com/api/v4/channels/{channel}"
    res = requests.get(url)
    emotes += res.json()["emotes"]

print(emotes)
for emoji in emotes:
    print(emoji["code"], emoji["id"])
    emojis[emoji["code"]] = (emoji["id"], getEmojiSize(emoji["id"]))


with open('emojis.json', 'w') as f:
    json.dump(emojis, f)
