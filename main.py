"""
Removes from Telegram channel's chat users that in chat but not in channel.
Can use with @donate subscription channels.
"""
import logging
import os
import re
import time
import urllib.parse
from enum import Enum
import asyncio

from pathlib import Path

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import User
from telethon import events

from telegram import Bot

from config import system_config

logging.basicConfig()
logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.DEBUG
)

BOT_USERNAME = '@OK1NewsBot'

channels = {
    "get": "-1001859259587",  # Channel 1
    "post": "-1001611862282",  # Channel 2
}


class AirAlerts(Enum):
    link = 'https://t.me/Trial_channel1'  # TODO change to 'https://t.me/air_alert_ua'
    # link = 'https://t.me/air_alert_ua'
    chat_id = 1859259587  # TODO change to 1766138888
    # chat_id = 1766138888
    vin_alert_start = 'Повітряна тривога в Вінницька область.'
    vin_alert_end = 'Відбій тривоги в Вінницька область.'


class VinODA(Enum):
    link = 'https://t.me/VinnytsiaODA'
    chat_id = 1392388295


class ETrivoga(Enum):
    link = 'https://t.me/UkraineAlarmSignal'
    chat_id = 1502899255

    alert_end = '🟢 Вінницька обл.'
    alert_start = '🚨 Вінницька обл.'
    gen_msg = '📢 Вінницька обл.'
    important_msg = '⚠️ Вінницька обл.'


class Ok1NewsChannel(Enum):  # TODO change to OK + add bot to OK
    link = 'https://t.me/Trail_Channel_2'
    chat_id = -1001611862282
    # chat_id = 1611862282


# Register `events.NewMessage` before defining the client.
# Once you have a client, `add_event_handler` will use this event.
# , pattern=r'(#Вінницька_область)')
@events.register(events.NewMessage(chats=[AirAlerts.chat_id.value]))  # 1766138888
async def alert_handler(event):
    print('event')  # TODO logging

    # Roadmap
    if client.alert_status:
        # post all notifications from AirAlerts
        if AirAlerts.vin_alert_end.value in event.raw_text:
            client.alert_status = False
            await bot.send_photo(
                chat_id=Ok1NewsChannel.chat_id.value,
                photo=Path('static/alert_end.jpg'),
                caption='🟢 Відбій тривоги на Вінниччині'
                )

    else:
        # post all notifications from Vin
        if '#Вінницька_область' in event.raw_text:
            if AirAlerts.vin_alert_start.value in event.raw_text:
                client.alert_status = True
                await bot.send_photo(
                    chat_id=Ok1NewsChannel.chat_id.value,
                    photo=Path('static/alert_start.jpg'),
                    caption='🔴 Повітряна тривога на Вінниччині'
                )


def get_default_alert_status():
    # TODO if no client.alert_status: parse last message of air_alert_ua channel
    ...


@events.register(events.NewMessage(chats=[ETrivoga.chat_id.value]))
async def event_handler(event):
    alert_end = '🟢 Вінницька обл.'
    alert_start = '🚨 Вінницька обл.'
    gen_msg = '📢 Вінницька обл.'
    important_msg = '⚠️ Вінницька обл.'

    async def alert():
        if client.alert_status:
            if alert_start in event.raw_text or alert_end in event.raw_text:
                return

            await bot.send_message(
                chat_id=Ok1NewsChannel.chat_id.value,
                text=event.raw_text
            )

        elif gen_msg in event.raw_text or important_msg in event.raw_text:
            await bot.send_message(
                chat_id=Ok1NewsChannel.chat_id.value,
                text=event.raw_text
            )

    await alert()


@events.register(events.NewMessage(chats=[VinODA.chat_id.value]))
async def message_handler(event):
    late_time_1 = '⏳З 00:00 розпочалася комендантська година. Вона триватиме до 5:00.'
    late_time_2 = '⏳З 23:00 розпочалася комендантська година. Вона триватиме до 5:00.'

    if late_time_1 in event.raw_text:
        await bot.send_photo(
            chat_id=Ok1NewsChannel.chat_id.value,
            photo=Path('static/late_time_00_05.jpg'),
            caption=event.raw_text
        )
    elif late_time_2 in event.raw_text:
        await bot.send_photo(
            chat_id=Ok1NewsChannel.chat_id.value,
            photo=Path('static/late_time_23_05.jpg'),
            caption=event.raw_text
        )
    else:
        await bot.send_message(
            chat_id=Ok1NewsChannel.chat_id.value,
            text=event.raw_text
        )


if __name__ == "__main__":
    client = TelegramClient(
        "anon", system_config.TG_API_ID, system_config.TG_API_HASH
    )

    bot = Bot(token=system_config.TG_BOT_TOKEN)

    with client.start(phone=system_config.PHONE_NUMBER):

        client.alert_status = False

        client.add_event_handler(alert_handler)
        client.add_event_handler(event_handler)
        client.add_event_handler(message_handler)

        client.run_until_disconnected()
