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
import requests

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

async def fetch_ids(input_file, output_file):
    logger.info('Starting the client...')
    await client.start(phone)
    logger.info('Client started.')

    logger.info(f'Reading input file: {input_file}')
    input_df = pd.read_csv(input_file)

    data = []
    for _, row in input_df.iterrows():
        chat_id = row['Chat ID']
        logger.info(f'Processing channel with ID: {chat_id}')
        try:
            channel_entity = await client.get_entity(chat_id)
            full_channel = await client(GetFullChannelRequest(channel_entity))
            followers = full_channel.full_chat.participants_count
            channel_link = f"https://t.me/{channel_entity.username}" if channel_entity.username else "No public link"
            data.append((channel_entity.title, channel_link, followers, chat_id))
        except ValueError:
            logger.error(f'Cannot find any entity corresponding to "{chat_id}". Skipping...')

    df = pd.DataFrame(data, columns=["Channel Name", "Channel Link", "Followers", "Chat ID"])
    df.to_csv(output_file, index=False)
    logger.info(f'Data written to {output_file}')

parser = argparse.ArgumentParser(description='Fetch Telegram channel IDs.')
parser.add_argument('--mode', choices=['fetch', 'parse', 'ids'], required=True, help='The operation mode.')
parser.add_argument('--input_file', help='An input CSV file with channel names and links or chat IDs.')
parser.add_argument('--output_file', default='channel_info.csv', help='The output CSV file.')

args = parser.parse_args()

with client:
    if args.mode == 'fetch':
        client.loop.run_until_complete(fetch_channels(args.output_file))
    elif args.mode == 'parse':
        if args.input_file is None:
            raise ValueError('The --input_file argument is required in parse mode.')
        client.loop.run_until_complete(parse_file(args.input_file, args.output_file))
    elif args.mode == 'ids':
        if args.input_file is None:
            raise ValueError('The --input_file argument is required in ids mode.')
        client.loop.run_until_complete(fetch_ids(args.input_file, args.output_file))
