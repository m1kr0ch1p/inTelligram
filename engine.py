import os
import asyncio
import details as ds
import requests
from telethon import TelegramClient, types, sync
from telethon.tl.functions.messages import GetHistoryRequest
from colorama import Fore, Style
from datetime import datetime


# variaveis de usuario para gerar a sessao do Telegram
api_id = ds.apiID
api_hash = ds.apiHash
phone = ds.number
client = TelegramClient(phone, api_id, api_hash)
channel_list = []
channel_list.append(input(str('Give me the Channel URL:\n')))

# channel_list = [-10000000000000]

# Faz o download de arquivos postados
async def content_downloader(channel_name, output_directory):
    async with client:
        # Recebe o nome do canal
        channel = await client.get_entity(channel_name)
        offset_id = 0
        limit = 100
        all_messages = []
        total_messages = 0

        while True:
            # Coleta o history do canal
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

                    # Verifica a extensão do arquivo
                    if file_name.lower().endswith(('.txt', '.zip', '.rar', '.jpg', '.png', '.pdf')):
                        file_path = os.path.join(output_directory, file_name)

                        # Verifica se o arquivo já foi baixado e realiza o download
                        if not os.path.exists(file_path):
                            await client.download_media(message, file_path)
                            print(f'{file_name} downloaded in {output_directory}.')
                        else:
                            print(f'{file_name} already exists.')

            all_messages.extend(messages)
            if len(messages) < limit:
                break

            offset_id = messages[-1].id
            total_messages = len(all_messages)

# Faz o scrape no canal e coleta os dados
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


# Recebe a URL do canal, define os nomes de diretorio e de arquivo e os dados coletados das mensagens
async def collect():
    import csv
    import pandas as pd
    from analytics import analyse

    for channel_name in channel_list:
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            # Descomente caso queira definir os canais por IDs
            #channel_name_filtered = str(channel_name).replace("-","")

            # Descomente caso queira definir os canais por links
            channel_name_filtered = channel_name.rsplit("/",1)[-1]

            # Define diretorio de saida
            output_directory = f'CaseFiles/{channel_name_filtered}'
            # Verifica se o diretorio ja existe / nomeia o diretorio
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            # nomeia o arquivo
            csv_filename = f'{output_directory}/{channel_name_filtered}_{today}.csv'
            print(f'[+] Scraping content from {Fore.LIGHTYELLOW_EX}{channel_name}{Style.RESET_ALL}...')

            # Executa a funcao scrape_channel_content com o canal indicado

            content = await scrape_channel_content(channel_name)

            # Armazena os dados do canal em arquivo csv
            if content:
                df = pd.DataFrame(content, columns=['Text', 'Username', 'First Name', 'Last Name', 'User ID', 'Views', 'message_url'])
                try:
                    df.to_csv(csv_filename, index=False)
                    print(f'[!] Successfully scraped and saved content to {Fore.LIGHTYELLOW_EX}{csv_filename}{Style.RESET_ALL}.')
                except Exception as e:
                    print(f"[-] An error occurred while saving to CSV: {Fore.RED}{e}{Style.RESET_ALL}")

            else:
               print(f'{Fore.RED}No content scraped.{Style.RESET_ALL}')

            # Executa a funcao content_downloader para baixar arquivos postados
            try:
                await content_downloader(channel_name, output_directory)
            except Exception as e:
                print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")


        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")

        analyse(csv_filename,channel_name_filtered)
