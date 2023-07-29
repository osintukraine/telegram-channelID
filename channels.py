from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel
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
    channels = [entity for entity in dialogs if isinstance(entity.entity, Channel)]
    
    data = []
    for channel in channels:
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

with client:
    client.loop.run_until_complete(main())
