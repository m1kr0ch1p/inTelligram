import os
import sys
sys.path.append('engines/')
import asyncio
import details as ds
from telethon import TelegramClient, types, sync
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style


# User's variable to create Telegram session
api_id = ds.apiID
api_hash = ds.apiHash
phone = ds.number
client = TelegramClient(phone, api_id, api_hash)

# Download posted files
async def content_downloader(channel_name, output_directory):
    async with client:
        # Get channel name
        channel = await client.get_entity(channel_name)
        offset_id = 0
        limit = 100
        all_messages = []
        total_messages = 0

        while True:
            # Collect channel history
            history = await client(GetHistoryRequest(
                peer=channel,
                offset_id=offset_id, offset_date=None,
                add_offset=0, limit=limit,
                max_id=0, min_id=0, hash=0))
            messages = history.messages

            for message in messages:
                if message.document:
                    file_name = None

                    for attr in message.document.attributes:
                        if hasattr(attr, 'file_name'):
                            file_name = attr.file_name
                            break

                    if not file_name:
                        file_name = f'document_{message.id}'

                    # Verify files extension
                    if file_name.lower().endswith(('.txt', '.zip', '.rar', '.jpg', '.png', '.pdf')):
                        downloaded_files = f'{output_directory}/downloaded_files'
                        if not os.path.exists(output_directory):
                            os.makedirs(output_directory)

                        file_path = os.path.join(downloaded_files, file_name)
                        # Check if files were previously downloaded
                        if not os.path.exists(file_path):
                            await client.download_media(message, file_path)
                            print(f'[+] {file_name} downloaded in {downloaded_files}.')
                        else:
                            print(f'[!] {file_name} already exists.')

            all_messages.extend(messages)
            if len(messages) < limit:
                break

            offset_id = messages[-1].id
            total_messages = len(all_messages)

# Scrapping channel and collecting data
async def scrape_channel_content(channel_name):
    async with client:
        try:
            entity = await client.get_entity(channel_name)
            content = []
            post_count = 0

            async for post in client.iter_messages(entity):
                post_count += 1

                text = post.text or ""
                if sender := post.sender:
                    if isinstance(sender, sync.types.User):
                        username = sender.username or "N/A"
                        first_name = sender.first_name or "N/A"
                        last_name = sender.last_name if sender.last_name else "N/A"
                        user_id = sender.id
                    else:
                        username = "N/A"
                        first_name = "N/A"
                        last_name = "N/A"
                        user_id = "N/A"
                else:
                    username = "N/A"
                    first_name = "N/A"
                    last_name = "N/A"
                    user_id = "N/A"

                views = post.views or "N/A"
                message_url = f"https://t.me/{channel_name}/{post.id}"

                content.append((text, username, first_name, last_name, user_id, views, message_url))
            return content

        except Exception as e:
            print(f"An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []

# Gets channel URL, set collected data, directory and file names 
async def collect():
    import pandas as pd
    from analytics import analyse
    from datetime import datetime

    for channel_name in channel_list:
        try:
            today = datetime.now().strftime("%Y-%m-%d")

            # Gives channel name to directory
            channel_name_filtered = channel_name.rsplit("/",1)[-1]
            # Defines output for files store
            output_directory = f'CaseFiles/{channel_name_filtered}'

            # Verify or creates directory
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            # Gives file name
            csv_filename = f'{output_directory}/{channel_name_filtered}_{today}.csv'
            print(f'[+] Scraping content from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')

            # runs scrape_channel_content function
            content = await scrape_channel_content(channel_name)

            # Store data in a csv file
            if content:
                df = pd.DataFrame(content, columns=['Text', 'Username', 'First Name', 'Last Name', 'User ID', 'Views', 'message_url'])
                try:
                    df.to_csv(csv_filename, index=False)
                    print(f'[!] Successfully scraped and saved content to {Fore.LIGHTYELLOW_EX}{csv_filename}{Style.RESET_ALL}.')
                except Exception as e:
                    print(f"[-] An error occurred while saving to CSV: {Fore.RED}{e}{Style.RESET_ALL}")

            else:
               print(f'{Fore.RED}No content scraped.{Style.RESET_ALL}')
            

            # DOwnloads shared files
            try:
                await content_downloader(channel_name, output_directory)
            except Exception as e:
                print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            

        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")

        await analyse(csv_filename,channel_name_filtered)

asyncio.run(collect())


# TODO - https://github.com/sockysec/Telerecon/blob/main/metadata.py
# https://spacy.io/usage/models