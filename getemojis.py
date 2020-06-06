import json
import logging
import requests
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


emojis = []

with open('emojis.json', 'w') as f:
    """for i in range(0, 20):
        url = "https://api.twitchemotes.com/api/v4/emotes?id=" + ",".join(map(str, range(i*10+1, i*10+11)))
        print(url)
        res = requests.get(url)
        part = res.json()
        print(res)
        emojis += part
"""
    url = "https://api.twitchemotes.com/api/v4/channels/0"
    res = requests.get(url)
    emotes = res.json()["emotes"]
    print(emotes)
    emojis += emotes

    json.dump(emojis, f)
