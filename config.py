import os
from dotenv import load_dotenv

load_dotenv()


class SystemConfig:
    TG_API_ID = int(os.environ["TG_API_ID"])
    TG_API_HASH = os.environ["TG_API_HASH"]
    TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
    TG_CHANNEL_ID = int(os.environ["TG_CHANNEL_ID"])

    PHONE_NUMBER = os.environ["PHONE_NUMBER"]


class AlertChannelConfig:
    VinODA_ID = int(os.environ["VinODA_CHANNEL_ID"])
    VinODA_LINK = os.environ["VinODA_CHANNEL_LINK"]

    AirAlerts_ID = int(os.environ["AirAlerts_CHANNEL_ID"])
    AirAlerts_LINK = os.environ["AirAlerts_CHANNEL_LINK"]

    ETrivoga_ID = int(os.environ["ETrivoga_CHANNEL_ID"])
    ETrivoga_LINK = os.environ["ETrivoga_CHANNEL_LINK"]

    KPS_ID = int(os.environ["KPS_CHANNEL_ID"])
    KPS_LINK = os.environ["KPS_CHANNEL_LINK"]


class ChannelConfig:
    POST_ID = int(os.environ["POST_CHANNEL_ID"])
    POST_LINK = os.environ["POST_CHANNEL_LINK"]


system_config = SystemConfig()
alert_config = AlertChannelConfig()
post_config = ChannelConfig()

