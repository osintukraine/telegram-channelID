import os
import csv
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel
import logging
import colorlog

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')

# Set up the logger
logger = logging.getLogger('telegram_script')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        'DEBUG':    'cyan',
        'INFO':     'green',
        'WARNING':  'yellow',
        'ERROR':    'red',
        'CRITICAL': 'red',
    }
)

handler.setFormatter(formatter)
logger.addHandler(handler)

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    logger.info('Starting the client...')
    await client.start(phone)
    logger.info('Client started.')

    logger.info('Getting dialogs...')
    dialogs = await client.get_dialogs()
    logger.info('Dialogs retrieved.')

    channels = [entity for entity in dialogs if isinstance(entity.entity, Channel)]
    
    data = []
    for channel in channels:
        logger.info(f'Processing channel: {channel.entity.title}')
        full_channel = await client(GetFullChannelRequest(channel.entity))
        channel_link = f"https://t.me/{channel.entity.username}" if channel.entity.username else "No public link"
        followers = full_channel.full_chat.participants_count
        chat_id = channel.entity.id
        data.append((channel.entity.title, channel_link, followers, chat_id))
    
    data.sort()  # Sort by channel name

    with open('channel_info.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Channel Name", "Channel Link", "Followers", "Chat ID"])
        writer.writerows(data)

    logger.info('Data written to channel_info.csv')

with client:
    client.loop.run_until_complete(main())
