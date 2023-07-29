import os
import csv
import argparse
import pandas as pd
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

async def fetch_channels(output_file):
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

    df = pd.DataFrame(data, columns=["Channel Name", "Channel Link", "Followers", "Chat ID"])
    df.to_csv(output_file, index=False)
    logger.info(f'Data written to {output_file}')

async def parse_file(input_file, output_file):
    logger.info('Starting the client...')
    await client.start(phone)
    logger.info('Client started.')

    logger.info(f'Reading input file: {input_file}')
    input_df = pd.read_csv(input_file)

    data = []
    for _, row in input_df.iterrows():
        channel_link = row['Channel Link']
        channel_name = row['Channel Name']
        logger.info(f'Processing channel: {channel_name}')
        channel_entity = await client.get_entity(channel_link)
        full_channel = await client(GetFullChannelRequest(channel_entity))
        followers = full_channel.full_chat.participants_count
        chat_id = channel_entity.id
        data.append((channel_name, channel_link, followers, chat_id))

    df = pd.DataFrame(data, columns=["Channel Name", "Channel Link", "Followers", "Chat ID"])
    df.to_csv(output_file, index=False)
    logger.info(f'Data written to {output_file}')

parser = argparse.ArgumentParser(description='Fetch Telegram channel IDs.')
parser.add_argument('--mode', choices=['fetch', 'parse'], required=True, help='The operation mode.')
parser.add_argument('--input_file', help='An input CSV file with channel names and links.')
parser.add_argument('--output_file', default='channel_info.csv', help='The output CSV file.')

args = parser.parse_args()

with client:
    if args.mode == 'fetch':
        client.loop.run_until_complete(fetch_channels(args.output_file))
    elif args.mode == 'parse':
        if args.input_file is None:
            raise ValueError('The --input_file argument is required in parse mode.')
        client.loop.run_until_complete(parse_file(args.input_file, args.output_file))
