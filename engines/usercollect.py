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

# Session elements
api_id = ds.apiID
api_hash = ds.apiHash
phone_number = ds.number
client = TelegramClient(phone_number, api_id, api_hash)

# Loads a channel list from file
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Collects user's data
async def get_user_data(username):
    try:
        user = await client.get_entity(username)

        # getting data
        username = user.username or 'N/A'
        first_name = user.first_name or 'N/A'
        last_name = user.last_name or 'N/A'
        user_id = user.id
        phone = user.phone if user.phone else "N/A"
                
        all_info = await client(GetFullUserRequest(username)) # using GetFullUserRequest
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
        
        return user_info

    except FloodWaitError as e:
        print(f'Flood wait error: Must wait {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)
        return await get_user_data(username)

    except (UsernameInvalidError, UsernameNotOccupiedError):
        return None

    except Exception as e:
        print(f'An error occurred: {e}')
        return None

# Gets user's status
async def get_user_status(user):
    if user.status:
        if isinstance(user.status, UserStatusOffline):
            return f'Last seen: {user.status.was_online}'
        else:
            return "Online"
    return "Offline"

# Loads CSV file
async def save_to_csv(usernames, channel_name):

    # Gives channel name to directory
    channel_name_filtered = channel_name.rsplit("/",1)[-1]

    # Defines output for files store
    output_directory = f'CaseFiles/{channel_name_filtered}'

    # Verify or creates directory
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    filename = f'{output_directory}/{channel_name_filtered}_users.csv'

    print(f"[+] Collecting usernames's data from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...")
    results = []
    for username in usernames:
        user_data = await get_user_data(username)
        if user_data:
            results.append(user_data)

    if results:
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f'Data saved in {filename}')
    else:
        print('[-] There is no data to write.')

# Lists usernames from channel
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
