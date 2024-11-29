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


# Configurações da sessão
api_id = ds.apiID
api_hash = ds.apiHash
phone_number = ds.number
client = TelegramClient(phone_number, api_id, api_hash)

# Carrega a lista de canais a partir de um arquivo
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Coleta dados do usuário
async def get_user_data(username, output_directory):
    try:
        user = await client.get_entity(username)

        # Coleta informações do usuário
        username = user.username or 'N/A'
        first_name = user.first_name or 'N/A'
        last_name = user.last_name or 'N/A'
        user_id = user.id
        phone = user.phone if user.phone else "N/A"
        all_info = await client(GetFullUserRequest(username))
        bio = all_info.full_user.about or "N/A"
        birth = all_info.full_user.birthday if all_info.full_user.birthday else "N/A"
        
        user_info = {
            'Username': username,
            'First Name': first_name,
            'Last Name': last_name,
            'User ID': user_id,
            'Phone': phone,
            'Bio': bio,
            'Birthday': birth,
        }

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

# Salva os dados em um arquivo CSV
async def save_to_csv(usernames, channel_name_filtered, output_directory):
    filename = f'{output_directory}/{channel_name_filtered}_users.csv'

    print(f"[+] Collecting usernames's data from {channel_name_filtered}...")
    results = []
    
    for username in usernames:
        user_data = await get_user_data(username, output_directory)
        if user_data:
            results.append(user_data)

    if results:
        # Escreve os dados no arquivo CSV
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        print(f'Data saved in {filename}')
    else:
        print('[-] There is no data to write.')

# Lista os nomes de usuários do canal
async def list_names():
    await client.start()

    channel_list = load_channel_list()

    for channel_name in channel_list:
        channel_name_filtered = channel_name.rsplit("/", 1)[-1]
        
        # Define o diretório de saída para os arquivos armazenados
        output_directory = f'CaseFiles/{channel_name_filtered}'
        
        # Verifica ou cria diretórios
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        try:
            channel = await client.get_entity(channel_name)
            usernames = [user.username for user in await client.get_participants(channel) if user.username]
            await save_to_csv(usernames, channel_name_filtered, output_directory)
        except Exception as e:
            print(f'Error to process channel {channel_name}: {e}')

# Executa a função list_names
with client:
    client.loop.run_until_complete(list_names())
