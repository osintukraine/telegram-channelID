from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import Channel, Chat, User
import csv
from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.getenv('API_ID')
api_hash = os.getenv('API_HASH')
phone = os.getenv('PHONE')

client = TelegramClient('session_name', api_id, api_hash)

async def main():
    await client.start(phone)
    dialogs = await client.get_dialogs()
    channels = [entity for entity in dialogs.entity if isinstance(entity, Channel)]
    
    data = []
    for channel in channels:
        full_channel = await client(GetFullChannelRequest(channel))
        channel_link = f"https://t.me/{channel.username}" if channel.username else "No public link"
        followers = full_channel.full_chat.participants_count
        chat_id = channel.id
        data.append((channel.title, channel_link, followers, chat_id))
    
    data.sort()  # Sort by channel name

    with open('channel_info.csv', 'w', newline='') as file
