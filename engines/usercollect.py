from telethon import TelegramClient
from telethon.errors import FloodWaitError, UsernameInvalidError, UsernameNotOccupiedError
from telethon.tl.types import UserStatusOffline
from telethon.tl.functions.users import GetFullUserRequest
import sys
sys.path.append('engines/')
import csv
import asyncio
import details as ds
import os
from colorama import Fore, Style

# Set session
api_id = ds.apiID
api_hash = ds.apiHash
phone_number = ds.number
client = TelegramClient(phone_number, api_id, api_hash)

# Load channel list in fule
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Collect users' data and looad in CSV
async def get_user_data(username, writer):
    try:
        user = await client.get_entity(username)

        # Get users' data
        username = user.username or 'N/A'
        first_name = user.first_name or 'N/A'
        last_name = user.last_name or 'N/A'
        user_id = user.id
        phone = user.phone if user.phone else "N/A"
        
        all_info = await client(GetFullUserRequest(username))
        bio = all_info.full_user.about or "N/A"
        profile_photo = all_info.full_user.profile_photo if all_info.full_user.profile_photo else "N/A"
        birth = all_info.full_user.birthday if all_info.full_user.birthday else "N/A"
        status = user.status
        
        user_info = {
            'Username': username,
            'First Name': first_name,
            'Last Name': last_name,
            'User ID': user_id,
            'Phone': phone,
            'Bio': bio,
            'Profile Photo': profile_photo,
            'Birthday': birth,
            'Status': status
        }

        print(f'-> {username} - {first_name} {last_name} - ID: {user_id} - Phone: {phone}')
        
        # Load data in csv file 
        writer.writerow(user_info)

    except FloodWaitError as e:
        print(f'Flood wait error: Must wait {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)
        return await get_user_data(username, writer)

    except (UsernameInvalidError, UsernameNotOccupiedError):
        return None

    except Exception as e:
        print(f'An error occurred: {e}')
        return None

# Save data in CSV
async def save_to_csv(usernames, channel_name):
    channel_name_filtered = channel_name.rsplit("/", 1)[-1]
    output_directory = f'CaseFiles/{channel_name_filtered}'

    # VVerify or create output directory
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    filename = f'{output_directory}/{channel_name_filtered}_users.csv'

    print(f"[+] Collecting usernames's data from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...")
    
    with open(filename, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['Username', 'First Name', 'Last Name', 'User ID', 'Phone', 'Bio', 'Profile Photo', 'Birthday', 'Status'])
        writer.writeheader()
        
        for username in usernames:
            await get_user_data(username, writer)

    print(f'Data saved in {filename}')

# List channel's usernam
async def list_names():
    await client.start()
    
    channel_list = load_channel_list()
    
    for channel_name in channel_list:
        try:
            channel = await client.get_entity(channel_name)
            usernames = [user.username for user in await client.get_participants(channel) if user.username]
            await save_to_csv(usernames, channel_name)
        except Exception as e:
            print(f'Error to process channel {channel_name}: {e}')

# Run list_names function
with client:
    client.loop.run_until_complete(list_names())
