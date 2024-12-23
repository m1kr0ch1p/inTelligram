from telethon import TelegramClient, errors
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerUser, ChannelParticipantsSearch
import sys
import csv
import asyncio
import os
from colorama import Fore, Style

sys.path.append('engines/')
import details as ds

# Session configuration
api_id = ds.apiID
api_hash = ds.apiHash
phone_number = ds.number
client = TelegramClient(phone_number, api_id, api_hash)

def load_channel_list(file_path='engines/channels.txt'):
    """Loads the channel list from a file"""
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

async def get_user_data(username, output_directory, writer):
    """Collects user data with error handling"""
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            user = await client.get_entity(username)
            photo_dir = os.path.join(output_directory, 'users_photos')
            os.makedirs(photo_dir, exist_ok=True)

            user_info = {
                'Username': user.username or 'N/A',
                'First Name': user.first_name or 'N/A',
                'Last Name': user.last_name or 'N/A',
                'User ID': user.id,
                'Phone': user.phone or "N/A",
                'Bio': (await client(GetFullUserRequest(InputPeerUser(user.id, user.access_hash)))).full_user.about or "N/A",
                'Birthday': (await client(GetFullUserRequest(InputPeerUser(user.id, user.access_hash)))).full_user.birthday or "N/A",
                'Status': user.status
            }

            profile_picture = 'Yes'
            if user.photo:
                profile_photo = await client.download_profile_photo(username, file=bytes)
                with open(os.path.join(photo_dir, f'{username}.jpg'), 'wb') as photo:
                    photo.write(profile_photo)
            else:
                profile_picture = 'No'

            print(f'-> {user_info["Username"]} - {user_info["First Name"]} {user_info["Last Name"]} - ID: {user_info["User ID"]} - Phone: {user_info["Phone"]} - Picture: {profile_picture}')
            writer.writerow(user_info)
            return
        except errors.FloodWaitError as e:
            print(f'Flood wait error: Must wait {e.seconds} seconds.')
            await asyncio.sleep(e.seconds)
        except (errors.UsernameInvalidError, errors.UsernameNotOccupiedError):
            print(f"Invalid username: {username}")
            return
        except (errors.NetworkError, errors.ConnectionError) as e:
            print(f'Connection error: {e}. Retrying in {retry_delay} seconds...')
            await asyncio.sleep(retry_delay)
        except Exception as e:
            print(f'An unexpected error occurred: {e}')
            if attempt < max_retries - 1:
                print(f'Retrying in {retry_delay} seconds...')
                await asyncio.sleep(retry_delay)
            else:
                print(f'Failed to get data for {username} after {max_retries} attempts')
                return

async def save_to_csv(usernames, channel_name_filtered, output_directory):
    """Saves data to a CSV file"""
    filename = os.path.join(output_directory, f'{channel_name_filtered}_users.csv')
    print(f"[+] Collecting usernames' data from {channel_name_filtered}...")

    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Username', 'First Name', 'Last Name', 'User ID', 'Phone', 'Bio', 'Birthday', 'Status'])
        writer.writeheader()

        for username in usernames:
            await get_user_data(username, output_directory, writer)

    print(f'Data saved in {filename}')

async def get_all_participants(channel):
    """Fetches all participants from a channel"""
    all_participants = []
    offset = 0
    limit = 200

    while True:
        try:
            participants = await client(GetParticipantsRequest(
                channel, ChannelParticipantsSearch(''), offset=offset,
                limit=limit, hash=0
            ))
            if not participants.users:
                break
            all_participants.extend(participants.users)
            offset += len(participants.users)
            await asyncio.sleep(2)
        except errors.FloodWaitError as e:
            print(f"Rate limit hit. Waiting for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)

    return all_participants

async def list_names():
    """Lists participant names and saves their data"""
    await client.start()
    channel_list = load_channel_list()

    for channel_name in channel_list:
        channel_name_filtered = channel_name.rsplit("/", 1)[-1]
        output_directory = os.path.join('CaseFiles', channel_name_filtered)
        os.makedirs(output_directory, exist_ok=True)

        try:
            channel = await client.get_entity(channel_name)
            all_participants = await get_all_participants(channel)
            print(f"Total participants collected: {len(all_participants)}")

            usernames = [user.username for user in all_participants if user.username]
            await save_to_csv(usernames, channel_name_filtered, output_directory)
        except Exception as e:
            print(f'Error processing channel {channel_name}: {e}')

with client:
    client.loop.run_until_complete(list_names())
