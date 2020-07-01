# TelegramTwitchEmoteBot

Share Twitch emotes with a Telegram chat through a quick inline command.

## Run

1. Copy crendentials.example.json to credentials.json.
```bash
cp crendentials.example.json credentials.json
```

2. Add you bot api key to credentials.json.

3. (**Optional**) Import initial bot data (see [Basic Emotes](#basic-emotes))
```bash
cp initial_bot_data bot_data
```

4. Install dependencies
```bash
pip install -r requirements.txt
```

5. Start the bot.
```bash
python bot.py
```

## Usage

### Add Emotes

To add emotes, you need to talk with the bot directly and use the following command:

```bash
/add <channelid>
``` 

#### Basic Emotes

Caching the basic emotes can take a long time. Because of that data for them is already included in the `initial_bot_data` file.
You can copy it to `bot_data` to import it into the bot. See step 3 in [Run](#run) for more information. 

### Inline
```bash
@bot-name <twitchemote>
```

| Argument    | Required | Explanation           | Example options        |
|-------------|----------|-----------------------|------------------------|
| twitchemote | required | Keyword for the emote | Kappa, Keepo, LUL, ... |
