import os
from dotenv import load_dotenv

load_dotenv()


class SystemConfig:
    TG_API_ID = int(os.environ["TG_API_ID"])
    TG_API_HASH = os.environ["TG_API_HASH"]
    TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
    TG_CHANNEL_ID = int(os.environ["TG_CHANNEL_ID"])

    BOT_USERNAME = os.environ["BOT_USERNAME"]
    PHONE_NUMBER = os.environ["PHONE_NUMBER"]


system_config = SystemConfig()
