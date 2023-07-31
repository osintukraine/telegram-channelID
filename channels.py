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
import xml.etree.ElementTree as ET
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


# Define your session file name
session_file = 'my_session'

# Create the client
client = TelegramClient(session_file, api_id, api_hash)

# Check if the session file exists
if not os.path.exists(session_file + '.session'):
    # If the session file doesn't exist, start the client with authentication
    client.start(phone, password)
else:
    # If the session file exists, start the client without authentication
    client.start()

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

from telethon.errors import UsernameInvalidError

from telethon.errors import FloodWaitError
import time

async def parse_file(input_file, output_file):
    logger.info('Starting the client...')
    await client.start(phone)
    logger.info('Client started.')

    logger.info(f'Reading input file: {input_file}')
    input_df = pd.read_csv(input_file)

    data = []
    for _, row in input_df.iterrows():
        channel_link = row['Channel Link']
        channel_name = row['Channel Name'] if pd.notnull(row['Channel Name']) else channel_link
        logger.info(f'Processing channel: {channel_name}')
        try:
            try:
                channel_entity = await client.get_entity(channel_link)
            except (ValueError, UsernameInvalidError) as e:
                logger.error(f'Failed to get entity for link "{channel_link}": {e}')
                continue
            full_channel = await client(GetFullChannelRequest(channel_entity))
            followers = full_channel.full_chat.participants_count
            chat_id = channel_entity.id
            # If channel name is empty in the CSV, fetch it from the Telegram API
            if pd.isnull(row['Channel Name']):
                channel_name = channel_entity.title
            data.append((channel_name, channel_link, followers, chat_id))
        except FloodWaitError as e:
            logger.error(f'Hit rate limit, sleeping for {e.seconds} seconds')
            time.sleep(e.seconds)
            continue
        except ValueError:
            logger.error(f'Cannot find any entity corresponding to "{channel_link}". Skipping...')

    df = pd.DataFrame(data, columns=["Channel Name", "Channel Link", "Followers", "Chat ID"])
    df.to_csv(output_file, index=False)
    logger.info(f'Data written to {output_file}')


async def parse_opml(input_file, output_file):
    logger.info('Starting the client...')
    await client.start(phone)
    logger.info('Client started.')

    logger.info(f'Reading input file: {input_file}')
    response = requests.get(input_file)
    root = ET.fromstring(response.content)

    data = []
    for outline in root.iter('outline'):
        channel_link = outline.attrib.get('htmlUrl')
        if channel_link:
            logger.info(f'Processing channel: {channel_link}')
            try:
                channel_entity = await client.get_entity(channel_link)
                full_channel = await client(GetFullChannelRequest(channel_entity))
                followers = full_channel.full_chat.participants_count
                chat_id = channel_entity.id
                data.append((channel_entity.title, channel_link, followers, chat_id))
            except ValueError:
                logger.error(f'Cannot find any entity corresponding to \"{channel_link}\". Skipping...')

    df = pd.DataFrame(data, columns=["Channel Name", "Channel Link", "Followers", "Chat ID"])
    df.to_csv(output_file, index=False)
    logger.info(f'Data written to {output_file}')

parser = argparse.ArgumentParser(description='Fetch Telegram channel IDs.')
parser.add_argument('--mode', choices=['fetch', 'parse', 'opml'], required=True, help='The operation mode.')
parser.add_argument('--input_file', help='An input CSV file with channel names and links or an OPML file URL.')
parser.add_argument('--output_file', default='channel_info.csv', help='The output CSV file.')

args = parser.parse_args()

with client:
    if args.mode == 'fetch':
        client.loop.run_until_complete(fetch_channels(args.output_file))
    elif args.mode == 'parse':
        if args.input_file is None:
            raise ValueError('The --input_file argument is required in parse mode.')
        client.loop.run_until_complete(parse_file(args.input_file, args.output_file))
    elif args.mode == 'opml':
        if args.input_file is None:
            raise ValueError('The --input_file argument is required in opml mode.')
        client.loop.run_until_complete(parse_opml(args.input_file, args.output_file))
