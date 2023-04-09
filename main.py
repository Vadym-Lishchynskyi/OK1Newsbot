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
from telethon.events.album import Album
from telethon.tl.types import User, MessageMediaPhoto, MessageMediaDocument

from telegram import Bot
import telegram


from config import system_config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.DEBUG
)


class AirAlerts(Enum):
    # link = 'https://t.me/Trial_channel1'  # TODO change to 'https://t.me/air_alert_ua'
    link = 'https://t.me/air_alert_ua'
    # chat_id = 1859259587  # TODO change to 1766138888
    chat_id = 1766138888
    vin_alert_start = 'Повітряна тривога в Вінницька область'
    vin_alert_end = 'Відбій тривоги в Вінницька область'


class VinODA(Enum):
    link = 'https://t.me/VinnytsiaODA'
    chat_id = 1392388295

    # TODO delete
    # link = 'https://t.me/Trial_channel1'
    # chat_id = 1859259587


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
@events.register(events.NewMessage(chats=[AirAlerts.chat_id.value]))
async def alert_handler(event):
    logger.info('event AirAlerts')

    if client.alert_status:
        # post all notifications from AirAlerts
        if AirAlerts.vin_alert_end.value in event.raw_text:
            client.alert_status = False
            await client.send_file(
                entity=Ok1NewsChannel.chat_id.value,
                file=Path('static/alert_end.jpg'),
                caption='🟢 Відбій тривоги на Вінниччині'
            )

    else:
        # post all notifications from Vin
        if '#Вінницька_область' in event.raw_text:
            if AirAlerts.vin_alert_start.value in event.raw_text:
                client.alert_status = True
                await client.send_file(
                    entity=Ok1NewsChannel.chat_id.value,
                    file=Path('static/alert_start.jpg'),
                    caption='🔴 Повітряна тривога на Вінниччині'
                )


def get_default_alert_status():
    # TODO if no client.alert_status: parse last message of air_alert_ua channel
    ...


@events.register(events.NewMessage(chats=[ETrivoga.chat_id.value]))
async def event_handler(event):
    logger.info('event ETrivoga')

    general_alert = '🚨'
    crimea_msg = '⚠️ Крим'

    alert_end = '🟢 Вінницька обл.'
    alert_start = '🚨 Вінницька обл.'
    gen_msg = '📢 Вінницька обл.'
    important_msg = '⚠️ Вінницька обл.'

    if general_alert in event.raw_text:
        return

    if crimea_msg in event.raw_text:
        await client.send_message(
            entity=Ok1NewsChannel.chat_id.value,
            message=event.text
        )
        return

    if client.alert_status:
        if alert_start in event.raw_text or alert_end in event.raw_text:
            return

        await client.send_message(
            entity=Ok1NewsChannel.chat_id.value,
            message=event.text
        )

    elif gen_msg in event.raw_text or important_msg in event.raw_text:
        await client.send_message(
            entity=Ok1NewsChannel.chat_id.value,
            message=event.text
        )


@events.register(events.NewMessage(chats=[VinODA.chat_id.value]))
async def vinoda_message_handler(event):
    logger.info('event VinODA')

    late_time_1 = '⏳З 00:00 розпочалася комендантська година. Вона триватиме до 5:00.'
    late_time_2 = '⏳З 23:00 розпочалася комендантська година. Вона триватиме до 5:00.'

    alert1 = '‼️🔴УВАГА! ПОВІТРЯНА ТРИВОГА!🔴‼️'
    alert2 = '🟩ВІДБІЙ ПОВІТРЯНОЇ ТРИВОГИ🟩'

    # skip grouped notifications
    if event.grouped_id is not None:
        return

    if alert1 in event.raw_text or alert2 in event.raw_text:
        return

    if late_time_1 in event.raw_text:
        await client.send_file(
            entity=Ok1NewsChannel.chat_id.value,
            file=Path('static/late_time_00_05.jpg'),
            caption=event.text
        )

    elif late_time_2 in event.raw_text:
        await client.send_file(
            entity=Ok1NewsChannel.chat_id.value,
            file=Path('static/late_time_23_05.jpg'),
            caption=event.text
        )
    else:
        await event.forward_to(Ok1NewsChannel.chat_id.value)


@events.register(events.album.Album(chats=[VinODA.chat_id.value]))
async def vinoda_group_message_handler(event):
    logger.info('event VinODA_group')

    # Forwarding the album as a whole to Ok1NewsChannel
    await event.forward_to(Ok1NewsChannel.chat_id.value)


if __name__ == "__main__":
    client = TelegramClient(
        "anon", system_config.TG_API_ID, system_config.TG_API_HASH
    )

    bot = Bot(token=system_config.TG_BOT_TOKEN)

    with client.start(phone=system_config.PHONE_NUMBER):
        client.alert_status = False

        client.add_event_handler(alert_handler)
        client.add_event_handler(event_handler)
        client.add_event_handler(vinoda_message_handler)
        client.add_event_handler(vinoda_group_message_handler)

        client.run_until_disconnected()
