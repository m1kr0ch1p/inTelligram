import asyncio
from telethon.tl.types import UserStatusOffline
from telethon import TelegramClient 
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import FloodWaitError, UsernameInvalidError, UsernameNotOccupiedError
import os
from details import apiID, apiHash, number
import datetime
import csv

client = TelegramClient(number, apiID, apiHash)

# set timestamp
async def format_timestamp(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).astimezone().strftime(
        '%Y-%m-%d %H:%M:%S %Z')

async def get_user_data(username):
    try:
        async with client:
            name = username
            user = await client.get_entity(name) # Using get_entity to collect user data

            # getting data
            username = user.username or 'N/A'
            first_name = user.first_name or 'N/A'
            last_name = user.last_name or 'N/A'
            user_id = user.id
            phone = user.phone if user.phone else "N/A"
                
            all_info = await client(GetFullUserRequest(name)) # using GetFullUserRequest
            bio = all_info.full_user.about or "N/A"
            profile_photo = all_info.full_user.profile_photo if all_info.full_user.profile_photo else "N/A"
            birth = all_info.full_user.birthday if all_info.full_user.birthday else "N/A"
            status = user.status
    
            # getting login account status
            if user.status:
                if isinstance(user.status, UserStatusOffline):
                    last_seen = user.status.was_online
                    last_seen_formatted = await format_timestamp(last_seen.timestamp())
                    status = last_seen_formatted
                else:
                    status = "Online"
            else:
                status = "Offline"

            # Return the collected data as a dictionary
            return {
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

    # handling request exceed
    except FloodWaitError as e:
        print(f'Flood wait error: Must wait {e.seconds} seconds.')
        await asyncio.sleep(e.seconds)  # Wait needed time
        return await get_user_data(username)  # Trying again
    
    # handling username erroes
    except (UsernameInvalidError, UsernameNotOccupiedError) as e:
        pass
    
    # handling error
    except Exception as e:
        print(f'An error occurred: {e}')
        return None  