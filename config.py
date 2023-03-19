import os
from dotenv import load_dotenv

load_dotenv()


class SystemConfig:
    TG_API_ID = int(os.environ["TG_API_ID"])
    TG_API_HASH = os.environ["TG_API_HASH"]
    # bot_token from Telegram's @BotFather
    TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
    # Id of your telegram channel. You can see it in web.telegram.org/z/,
    # add -100 to the string start.
    # For example, id in URL is 123, so use -100123 here
    TG_CHANNEL_ID = int(os.environ["TG_CHANNEL_ID"])


system_config = SystemConfig()
