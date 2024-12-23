import os
import sys
import asyncio
import details as ds
from telethon import TelegramClient, sync #, types
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style

sys.path.append('engines/')

# User's variable to create Telegram session
api_id = ds.apiID
api_hash = ds.apiHash
phone = ds.number
client = TelegramClient(phone, api_id, api_hash)

# Loads a channel list from file
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Download shared files
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
                    if file_name.lower().endswith(('.txt', '.zip', '.rar', '.jpg', '.png', '.pdf', '.doc', '.docx', '.xls')):
                        downloaded_files = f'{output_directory}/downloaded_files'
                        if not os.path.exists(output_directory):
                            os.makedirs(output_directory)

                        file_path = os.path.join(downloaded_files, file_name)
                        # Check if files were previously downloaded
                        if not os.path.exists(file_path):
                            await client.download_media(message, file_path)
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
                date = post.date.strftime("%Y-%m-%d %H:%M:%S%z") or "" # Get message date and time 

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

                content.append((date, text, username, first_name, last_name, user_id, views, message_url))
            return content

        except Exception as e:
            print(f"An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []

# Gets channel URL, set collected data, directory and file names 
async def collect():
    import pandas as pd
    #from datetime import datetime

    channel_list = load_channel_list()

    for channel_name in channel_list:
        try:
            #today = datetime.now().strftime("%Y-%m-%d")

            # Gives channel name to directory
            channel_name_filtered = channel_name.rsplit("/",1)[-1]

            # Defines output for files store
            output_directory = f'CaseFiles/{channel_name_filtered}'

            # Verify or creates directory
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            # Gives file name
            #csv_filename = f'{output_directory}/{channel_name_filtered}_{today}.csv'
            csv_filename = f'{output_directory}/{channel_name_filtered}.csv'
            print(f'[+] Scraping content from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')

            # runs scrape_channel_content function
            content = await scrape_channel_content(channel_name)

            # Store data in a csv file
            if content:
                df = pd.DataFrame(content, columns=['Date', 'Text', 'Username', 'First Name', 'Last Name', 'User ID', 'Views', 'message_url'])

                # converts Date to datetime
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

                # Handle abscent data
                df.dropna(subset=['Date'], inplace=True)

                # Add Hour Column to Dataframe
                df['Hour'] = df['Date'].dt.hour
                
                try:
                    df.to_csv(csv_filename, index=False)
                    print(f'[!] Successfully scraped and saved content to {Fore.LIGHTYELLOW_EX}{csv_filename}{Style.RESET_ALL}.')
                except Exception as e:
                    print(f"[-] An error occurred while saving to CSV: {Fore.RED}{e}{Style.RESET_ALL}")

            else:
               print(f'{Fore.RED}No content scraped.{Style.RESET_ALL}')
            
            # Downloads shared files
            try:
                print(f'[+] Downloading files from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')
                await content_downloader(channel_name, output_directory)
            except Exception as e:
                print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            
        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")

asyncio.run(collect())
