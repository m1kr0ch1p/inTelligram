from telethon import TelegramClient, errors
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import InputPeerUser, ChannelParticipantsSearch
import sys
import csv
import asyncio
import details as ds
import os
from colorama import Fore, Style

sys.path.append('engines/')

# Session elements
api_id = ds.apiID
api_hash = ds.apiHash
phone_number = ds.number
client = TelegramClient(phone_number, api_id, api_hash)

# Loads a channel list from file
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Collects user's data with improved error handling
async def get_user_data(username, output_directory, writer):
    max_retries = 3
    retry_delay = 5

    for attempt in range(max_retries):
        try:
            user = await client.get_entity(username)

            photo_dir = f'{output_directory}/users_photos'
            if not os.path.exists(photo_dir):
                os.makedirs(photo_dir)

            # getting data
            username = user.username or 'N/A'
            first_name = user.first_name or 'N/A'
            last_name = user.last_name or 'N/A'
            user_id = user.id
            phone = user.phone if user.phone else "N/A"
            all_info = await client(GetFullUserRequest(InputPeerUser(user_id, user.access_hash)))
            bio = all_info.full_user.about or "N/A"
            birth = all_info.full_user.birthday if all_info.full_user.birthday else "N/A"
            status = user.status

            # Prepare user info for CSV
            user_info = {
                'Username': username,
                'First Name': first_name,
                'Last Name': last_name,
                'User ID': user_id,
                'Phone': phone,
                'Bio': bio,
                'Birthday': birth,
                'Status': status
            }

            # Download user photo
            profile_picture = 'Yes'
            if user.photo:
                profile_photo = await client.download_profile_photo(username, file=bytes)
                with open(os.path.join(photo_dir, f'{username}.jpg'), 'wb') as photo:
                    photo.write(profile_photo)
            else:
                profile_picture = 'No'

            print(f'-> {username} - {first_name} {last_name} - ID: {user_id} - Phone: {phone} - Picture: {profile_picture}')

            # Write to CSV immediately after collecting data
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

# Loads CSV file and writes data directly to it
async def save_to_csv(usernames, channel_name_filtered, output_directory):
    filename = f'{output_directory}/{channel_name_filtered}_users.csv'

    print(f"[+] Collecting usernames's data from {channel_name_filtered}...")
    
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Username', 'First Name', 'Last Name', 'User ID', 'Phone', 'Bio', 'Birthday', 'Status'])
        writer.writeheader()

        for username in usernames:
            await get_user_data(username, output_directory, writer)

    print(f'Data saved in {filename}')


async def get_all_participants(channel):
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
            #print(f"Collected {len(all_participants)} participants so far...")
            await asyncio.sleep(2)  # Increased delay to respect rate limits
        except errors.FloodWaitError as e:
            print(f"Rate limit hit. Waiting for {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
    return all_participants

async def list_names():
    await client.start()

    channel_list = load_channel_list()

    for channel_name in channel_list:
        channel_name_filtered = channel_name.rsplit("/", 1)[-1]

        output_directory = f'CaseFiles/{channel_name_filtered}'
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        try:
            channel = await client.get_entity(channel_name)
            
            all_participants = await get_all_participants(channel)
            print(f"Total participants collected: {len(all_participants)}")

            usernames = [user.username for user in all_participants if user.username]
            await save_to_csv(usernames, channel_name_filtered, output_directory)

        except Exception as e:
            print(f'Error processing channel {channel_name}: {e}')

# Run list_names function
with client:
    client.loop.run_until_complete(list_names())
