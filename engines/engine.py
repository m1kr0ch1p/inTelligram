import os
import sys
import asyncio
from telethon import TelegramClient, sync
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style

sys.path.append('engines/')
import details as ds

# User's variables to create a Telegram session
api_id = ds.apiID
api_hash = ds.apiHash
phone = ds.number
client = TelegramClient(phone, api_id, api_hash)

def load_channel_list(file_path='engines/channels.txt'):
    """Loads the channel list from a file"""
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

async def content_downloader(channel_name, output_directory):
    """Downloads shared files from a Telegram channel"""
    async with client:
        channel = await client.get_entity(channel_name)
        offset_id = 0
        limit = 100
        all_messages = []

        while True:
            history = await client(GetHistoryRequest(
                peer=channel,
                offset_id=offset_id,
                offset_date=None,
                add_offset=0,
                limit=limit,
                max_id=0,
                min_id=0,
                hash=0
            ))
            messages = history.messages

            for message in messages:
                if message.document:
                    file_name = next(
                        (attr.file_name for attr in message.document.attributes if hasattr(attr, 'file_name')),
                        f'document_{message.id}'
                    )

                    if file_name.lower().endswith(('.txt', '.zip', '.rar', '.jpg', '.png', '.pdf', '.doc', '.docx', '.xls')):
                        downloaded_files = os.path.join(output_directory, 'downloaded_files')
                        os.makedirs(downloaded_files, exist_ok=True)
                        file_path = os.path.join(downloaded_files, file_name)

                        if not os.path.exists(file_path):
                            await client.download_media(message, file_path)
                            print(f'[+] {file_name} downloaded.')
                        else:
                            print(f'[!] {file_name} already exists.')

            all_messages.extend(messages)
            if len(messages) < limit:
                break
            offset_id = messages[-1].id

async def scrape_channel_content(channel_name):
    """Scrapes the content of a Telegram channel"""
    async with client:
        try:
            entity = await client.get_entity(channel_name)
            content = []

            async for post in client.iter_messages(entity):
                text = post.text or ""
                date = post.date.strftime("%Y-%m-%d %H:%M:%S%z") if post.date else ""
                sender = post.sender

                user_info = {
                    'Username': sender.username if sender and isinstance(sender, sync.types.User) else "N/A",
                    'First Name': sender.first_name if sender else "N/A",
                    'Last Name': sender.last_name if sender and sender.last_name else "N/A",
                    'User ID': sender.id if sender else "N/A",
                    'Views': post.views or "N/A",
                    'Message URL': f"https://t.me/{channel_name}/{post.id}"
                }

                content.append((date, text, user_info['Username'], user_info['First Name'], user_info['Last Name'], user_info['User ID'], user_info['Views'], user_info['Message URL']))

            return content

        except Exception as e:
            print(f"An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []

async def collect():
    """Collects data from specified Telegram channels"""
    import pandas as pd

    channel_list = load_channel_list()

    for channel_name in channel_list:
        try:
            channel_name_filtered = channel_name.rsplit("/", 1)[-1]
            output_directory = os.path.join('CaseFiles', channel_name_filtered)
            os.makedirs(output_directory, exist_ok=True)
            csv_filename = os.path.join(output_directory, f'{channel_name_filtered}.csv')

            print(f'[+] Scraping content from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')
            content = await scrape_channel_content(channel_name)

            if content:
                df = pd.DataFrame(content, columns=['Date', 'Text', 'Username', 'First Name', 'Last Name', 'User ID', 'Views', 'Message URL'])
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df.dropna(subset=['Date'], inplace=True)
                df['Hour'] = df['Date'].dt.hour

                try:
                    df.to_csv(csv_filename, index=False)
                    print(f'[!] Successfully scraped and saved content to {Fore.LIGHTYELLOW_EX}{csv_filename}{Style.RESET_ALL}.')
                except Exception as e:
                    print(f"[-] An error occurred while saving to CSV: {Fore.RED}{e}{Style.RESET_ALL}")
            else:
                print(f'{Fore.RED}No content scraped.{Style.RESET_ALL}')

            try:
                print(f'[+] Downloading files from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')
                await content_downloader(channel_name, output_directory)
            except Exception as e:
                print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")

        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")

asyncio.run(collect())
