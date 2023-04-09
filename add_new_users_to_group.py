import logging
from enum import Enum

from telethon.sync import TelegramClient
from telethon.tl.functions.channels import InviteToChannelRequest, JoinChannelRequest
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import User, MessageMediaPhoto, MessageMediaDocument, InputPhoneContact

from telegram import Bot

from config import system_config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

logging.basicConfig(
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=logging.DEBUG
)


class Channel(Enum):
    link = 'https://t.me/Trail_Channel_2'
    chat_id = -1001611862282


async def add_contact():
    # connect to the Telegram server
    await client.connect()

    # get the input entity for the user's phone number
    user_phone = '+380974773080'  # replace with the user's phone number
    user_entity = await client.get_input_entity(user_phone)

    # create a new contact with the user's information
    contact = InputPhoneContact(
        client_id=0,  # this can be any value
        phone=user_phone,
        first_name='Trial',
        last_name='User'
    )

    # add the contact to your Telegram contacts
    result = await client(ImportContactsRequest([contact]))

    await client(InviteToChannelRequest(
            Channel.chat_id.value,
            [user_entity]
        ))

    # disconnect from the Telegram server
    await client.disconnect()
    return result

if __name__ == "__main__":
    client = TelegramClient(
        "anon", system_config.TG_API_ID, system_config.TG_API_HASH
    )

    bot = Bot(token=system_config.TG_BOT_TOKEN)

    with client.start(phone=system_config.PHONE_NUMBER):

        client.loop.run_until_complete(add_contact())
