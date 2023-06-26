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

from config import (
    system_config,
    alert_config,
    post_config
)

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
fh = logging.FileHandler('status_logs.log')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(fh)


class KPSzsu(Enum):
    link = alert_config.KPS_LINK
    chat_id = alert_config.KPS_ID

    rocket_danger = '🚀 Вінницька область'  # https://t.me/kpszsu/2805
    airalert_info = 'Вінницька область'  # https://t.me/kpszsu/2702
    midUA_info = 'Центральні області'  # https://t.me/kpszsu/2765
    midUAs_info = 'центральних'  # https://t.me/kpszsu/2803


class AirAlerts(Enum):
    link = alert_config.AirAlerts_LINK
    chat_id = alert_config.AirAlerts_ID

    vin_alert_start = 'Повітряна тривога в Вінницька область'
    vin_alert_end = 'Відбій тривоги в Вінницька область'


class VinODA(Enum):
    link = alert_config.VinODA_LINK
    chat_id = alert_config.VinODA_ID


class ETrivoga(Enum):
    link = alert_config.ETrivoga_LINK
    chat_id = alert_config.ETrivoga_ID

    alert_end = '🟢 Вінницька обл.'
    alert_start = '🚨 Вінницька обл.'
    gen_msg = '📢 Вінницька обл.'
    important_msg = '⚠️ Вінницька обл.'


class Ok1NewsChannel(Enum):
    link = post_config.POST_LINK
    chat_id = post_config.POST_ID


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

    symbol_explosion = '⚠️'
    symbol_alert = '📢'

    vin_msg = 'Вінницька обл.'
    crimea_msg = 'Крим'

    def strip_msg(msg: str) -> str:
        to_strip = ['- будьте обережні', 'Будьте обережні!']

        for phrase in to_strip:
            msg = msg.rstrip(phrase)

        return msg

    if symbol_explosion in event.raw_text or symbol_alert in event.raw_text:
        message = strip_msg(event.text)
        if client.alert_status:
            await client.send_message(
                entity=Ok1NewsChannel.chat_id.value,
                message=message
            )
        else:
            if vin_msg in message or crimea_msg in message:
                await client.send_message(
                    entity=Ok1NewsChannel.chat_id.value,
                    message=message
                )


@events.register(events.NewMessage(chats=[KPSzsu.chat_id.value]))
async def kpszsu_handler(event):
    logger.info('event KPSzsu')

    def strip_kpszsumsg(msg: str) -> str:
        to_strip = ['⚠️Увага!', '⚠️ Увага!', 'Прямуйте в укриття!', 'Не ігноруйте сигнали повітряної тривоги!']

        for phrase in to_strip:
            msg = msg.replace(phrase, '')

        return msg

    if client.alert_status:
        if KPSzsu.midUA_info.value in event.raw_text \
                or KPSzsu.midUAs_info.value in event.raw_text \
                or KPSzsu.airalert_info.value in event.raw_text:
            message = strip_kpszsumsg(event.text)
            await client.send_message(
                entity=Ok1NewsChannel.chat_id.value,
                message=message
            )

    if KPSzsu.rocket_danger.value in event.raw_text:
        await client.send_message(
            entity=Ok1NewsChannel.chat_id.value,
            message='⚠️ Повітряні Сили ЗСУ повідомляють про загрозу ракетного удару по Вінниччині! Пройдіть в '
                    'безпечне місце!'
        )


@events.register(events.NewMessage(chats=[VinODA.chat_id.value]))
async def vinoda_message_handler(event):
    logger.info('event VinODA')

    late_time_1 = '⏳З 00:00 розпочалася комендантська година. Вона триватиме до 5:00.'
    late_time_2 = '⏳З 23:00 розпочалася комендантська година. Вона триватиме до 5:00.'

    alerts = [
        '‼️🔴УВАГА! ПОВІТРЯНА ТРИВОГА!🔴‼️',
        '🟩ВІДБІЙ ПОВІТРЯНОЇ ТРИВОГИ🟩',
        '🟢 Відбій тривоги на Вінниччині',
        '🔴 Повітряна тривога на Вінниччині'
    ]

    # skip grouped notifications
    if event.grouped_id is not None:
        return

    if event.raw_text.strip() in alerts:
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
        client.add_event_handler(kpszsu_handler)

        client.run_until_disconnected()
