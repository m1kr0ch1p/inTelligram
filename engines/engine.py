import os
import sys
import asyncio
from telethon import TelegramClient, sync, errors
from telethon.tl import types
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import rpcerrorlist
from colorama import Fore, Style
import pandas as pd
import csv
import random 
from time import sleep

sys.path.append('engines/')
import details as ds

# User's variables to create a Telegram session
api_id = ds.apiID
api_hash = ds.apiHash
phone = ds.number
client = TelegramClient(phone, api_id, api_hash)

# random time sleep
def time_delay():
    sleep_duration = random.randint(10, 20)
    sleep(sleep_duration)

# Turns User's status in a readable way
def get_human_readable_user_status(status: types.TypeUserStatus):
    match status:
        case types.UserStatusOnline():
            return "Currently online"
        case types.UserStatusOffline():
            return status.was_online.strftime("%Y-%m-%d %H:%M:%S %Z")
        case types.UserStatusRecently():
            return "Last seen recently"
        case types.UserStatusLastWeek():
            return "Last seen last week"
        case types.UserStatusLastMonth():
            return "Last seen last month"
        case _:
            return "Unknown"

# Prepares channels' URLs from channel list file
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r", encoding='utf-8') as file:
        return [line.strip() for line in file]

# Gets users' informations from channel
async def user_collect(channel_name, channel_name_filtered):

    # Collect user data and handle errors
    async def get_user_data(username, output_directory, writer):

        max_retries = 3
        retry_delay = 5

        for attempt in range(max_retries):
            try:
                time_delay()
                # Request username
                user = await client.get_entity(username)
                # Set usernames' avatars directory
                photo_dir = os.path.join(output_directory, 'users_photos')
                os.makedirs(photo_dir, exist_ok=True)

                # Getting available users' info (ID, Username, alias, phone, bio and birthday) to store in a CSV file. 
                user_info = {
                    'User_ID': user.id,
                    'Username': user.username or 'N/A',
                    'First_Name': user.first_name or 'N/A',
                    'Last_Name': user.last_name or 'N/A',
                    'Phone': user.phone or "N/A",
                    'Bio': (await client(GetFullUserRequest(types.InputPeerUser(user.id, user.access_hash)))).full_user.about or "N/A",
                    #'Birthday': (await client(GetFullUserRequest(types.InputPeerUser(user.id, user.access_hash)))).full_user.birthday or "N/A",
                    'Status': get_human_readable_user_status(user.status)
                }

                # Checks if there is profile picture and downloads it.
                profile_picture = 'Yes'
                if user.photo:
                    time_delay()
                    profile_photo = await client.download_profile_photo(username, file=bytes)
                    with open(os.path.join(photo_dir, f'{username}.jpg'), 'wb') as photo:
                        photo.write(profile_photo)
                else:
                    profile_picture = 'No'

                # Shows users' info in Stdout and stores in CSV file
                print(f'-> Username: {user_info["Username"]};  Name: {user_info["First_Name"]} {user_info["Last_Name"]};  ID: {user_info["User_ID"]};   Phone: {user_info["Phone"]};  Picture: {profile_picture}')
                writer.writerow(user_info)
                return
            except rpcerrorlist.FloodWaitError as e:
                print(f'Flood wait error: Must wait {e.seconds} seconds.')
                await asyncio.sleep(e.seconds)
            except (rpcerrorlist.UsernameInvalidError, rpcerrorlist.UsernameNotOccupiedError):
                print(f"Invalid username: {username}")
                return
            except Exception as e:
                print(f'An unexpected error occurred for {username}: {e}')
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    return

    # Save usernames' info in a csv file
    async def save_to_csv(usernames, channel_name_filtered, output_directory):

        filename = os.path.join(output_directory, f'{channel_name_filtered}_users.csv')
        print(f"[+] Collecting usernames' data from {channel_name_filtered}...")

        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            #writer = csv.DictWriter(file, fieldnames=['User_ID', 'Username', 'First_Name', 'Last_Name', 'Phone', 'Bio', 'Birthday', 'Status'])
            writer = csv.DictWriter(file, fieldnames=['User_ID', 'Username', 'First_Name', 'Last_Name', 'Phone', 'Bio', 'Status'])
            writer.writeheader()

            for username in usernames:
                await get_user_data(username, output_directory, writer)
                await asyncio.sleep(1)  # Adding delay for requests

        print(f'Data saved in {filename}')

    # Request all chat participants
    async def get_all_participants(channel):
        all_participants = []
        offset = 0
        limit = 1000
        hash = 0

        while True:
            try:
                participants = await client(GetParticipantsRequest(
                    channel=channel,
                    filter=types.ChannelParticipantsSearch(''),
                    offset=offset,
                    limit=limit,
                    hash=hash
                ))

                if not participants.users:
                    break

                all_participants.extend(participants.users)
                offset += len(participants.users)
                await asyncio.sleep(2)  # Respect limit rate to avoid FloodWaitError
            except errors.FloodWaitError as e:
                print(f"Rate limit hit. Waiting for {e.seconds} seconds")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
                break

        return all_participants

    # List participant names and saves their data
    async def list_names(channel_name, channel_name_filtered):

        await client.start()
        #channel_list = load_channel_list()

        output_directory = os.path.join('CaseFiles', channel_name_filtered)
        os.makedirs(output_directory, exist_ok=True)

        try:
            channel = await client.get_entity(channel_name)
            all_participants = await get_all_participants(channel)
            print(f"Total participants collected: {len(all_participants)}")

            # Including all users, even those without username or numeric usernames
            usernames = [user.id for user in all_participants]
            print(f"Usernames extracted: {len(usernames)}")
            await save_to_csv(usernames, channel_name_filtered, output_directory)
        except Exception as e:
            print(f'Error processing channel {channel_name}: {e}')

    await list_names(channel_name, channel_name_filtered)

# Function to download shared files according defined extensions
async def content_downloader(channel_name, output_directory):

    async with client:
        # Request channel
        channel = await client.get_entity(channel_name)
        offset_id = 0
        limit = 100
        all_messages = []

        while True:
            try:
                # List history messages in 'messages'
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

                # Iterate each message to find files
                for message in messages:
                    if message.document:
                        file_name = next(
                            (attr.file_name for attr in message.document.attributes if hasattr(attr, 'file_name')),
                            f'document_{message.id}'
                        )
                        # Download shared files from chat. YOU CAN SET YOUR INTEREST FILE EXTENSIONS HERE
                        if file_name.lower().endswith(('.txt', '.zip', '.rar', '.jpg', '.png', '.pdf', '.doc', '.docx', '.xls', '.ppt', '.pptx')):
                            downloaded_files = os.path.join(output_directory, 'downloaded_files')
                            os.makedirs(downloaded_files, exist_ok=True)
                            file_path = os.path.join(downloaded_files, file_name)

                            # Set shared files directory
                            if not os.path.exists(file_path):
                                time_delay()
                                await client.download_media(message, file_path)
                                print(f'[+] {file_name} downloaded.')
                            else:
                                print(f'[!] {file_name} already exists.')

                all_messages.extend(messages)
                if len(messages) < limit:
                    break
                offset_id = messages[-1].id

            except Exception as e:
               print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
               return []

# Scrape the content fo a Telegram Channel
async def scrape_channel_content(channel_name,output_directory):

    async with client:
        try:
            # Request chat entity
            entity = await client.get_entity(channel_name)

            # Write chat entity into a txt file
            output_file = open(f'{output_directory}/channel_info.txt','w', encoding='utf-8')
            output_file.write(str(entity))
            output_file.close()
            print(f'''===> Channel info:\n Id: {entity.id}\n Access hash: {entity.access_hash}\n Date: {entity.date}\n Title: {entity.title}\n Username: {entity.username}
 Creator: {entity.creator}\n Is gigagroup: {entity.gigagroup}\n Is megagroup: {entity.megagroup}\n Link: {entity.has_link}\n Geo: {entity.has_geo}\n''')

            # Open content list
            content = []


            # Collect usernames' messages
            async for post in client.iter_messages(entity):
                text = post.text or ""
                date = post.date.strftime("%Y-%m-%d %H:%M:%S%z") if post.date else ""
                sender = post.sender

                user_info = {
                    'Username': sender.username if sender and isinstance(sender, sync.types.User) else "N/A",
                    'User ID': sender.id if sender else "N/A",
                    'Views': post.views or "N/A",
                    'Message URL': f"https://t.me/{channel_name}/{post.id}"
                }

                # Append messages data to content list
                content.append((date, text, user_info['Username'], user_info['User ID'], user_info['Views'], user_info['Message URL']))
            return content

        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []

# Main function to collect data from chat's messages, members and shared files
async def collect():

    channel_list = load_channel_list()

    # Prepare directoriess and files to receive research data for each Telegram Chat
    for channel_name in channel_list:
        try:
            # Set directory and csv file to receive data
            channel_name_filtered = channel_name.rsplit("/", 1)[-1]
            output_directory = os.path.join('CaseFiles', channel_name_filtered)
            os.makedirs(output_directory, exist_ok=True)
            csv_filename = os.path.join(output_directory, f'{channel_name_filtered}.csv')
            print(f'[+] Scraping content from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')

            # Call the function that collects data from chat
            content = await scrape_channel_content(channel_name,output_directory)

            # Transcribe collect data (content) to csv file
            if content:
                df = pd.DataFrame(content, columns=['Date', 'Text', 'Username', 'User ID', 'Views', 'Message URL'])
                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df.dropna(subset=['Date'], inplace=True)
                df['Hour'] = df['Date'].dt.hour

                # Finish chat messages data dump
                try:
                    df.to_csv(csv_filename, index=False)
                    print(f'[!] Successfully scraped and saved content to {Fore.LIGHTYELLOW_EX}{csv_filename}{Style.RESET_ALL}.')
                except Exception as e:
                    print(f"[-] An error occurred while saving to CSV: {Fore.RED}{e}{Style.RESET_ALL}")
            else:
                print(f'{Fore.RED}No content scraped.{Style.RESET_ALL}')

            # Call the function that collect usernames' data
            await user_collect(channel_name, channel_name_filtered)

            # Dumps shared files from chat according defined extensions
            try:
                print(f'[+] Downloading files from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')
                await content_downloader(channel_name, output_directory)
            except Exception as e:
                print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")

        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
