import asyncio
from colorama import Fore, Style
import sys

# Banner
def banner():
    banner = f"""{Fore.BLUE}
    ██╗███╗   ██╗████████╗███████╗██╗     ██╗     ██╗ ██████╗ ██████╗  █████╗ ███╗   ███╗
    ██║████╗  ██║╚══██╔══╝██╔════╝██║     ██║     ██║██╔════╝ ██╔══██╗██╔══██╗████╗ ████║
    ██║██╔██╗ ██║   ██║   █████╗  ██║     ██║     ██║██║  ███╗██████╔╝███████║██╔████╔██║
    ██║██║╚██╗██║   ██║   ██╔══╝  ██║     ██║     ██║██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║
    ██║██║ ╚████║   ██║   ███████╗███████╗███████╗██║╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║
    ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝╚══════╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝{Style.RESET_ALL}\n"""
    print(banner)

# External IP banner
def ip_check():
    import json
    import requests

    try:
        webURL = 'http://ip-api.com/json/?fields=61439'
        json_data = requests.get(webURL).json()

        # JSON handling
        dataB = json.dumps(json_data)
        data = json.loads(dataB)

        # Getting informations
        country_code = data['countryCode']
        city = data['city']
        query = data['query']

        # Formatting
        formatted_info = f"{city}-{country_code} (IP Adress {query})"

        # Printing results
        print(f'[*] You are connected to Internet from {Fore.YELLOW}{formatted_info}{Style.RESET_ALL}\n')
    except Exception as e:
        print(f'{Fore.RED}[-] {e}{Style.RESET_ALL}')

# receive channels to collect and analyse
def ignite():
    global channel_list
    channel_list = []
    channel_file = 'engines/channels.txt'
    with open(channel_file, "r") as file:
        for channel in file:
            channel_list.append(channel.strip())

# create directories
def create_dirs():
    import os

    # creates directories for each channel
    for channel_name in channel_list:
        # Gives channel name to directory
        channel_name_filtered = channel_name.rsplit("/",1)[-1]
        # Defines output for files store
        output_directory = f'CaseFiles/{channel_name_filtered}'
        # Verify or creates directory
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)


def main():
    # Calling local functions
    banner()
    ip_check()
    ignite()
    create_dirs()

    # Calling data collector
    asyncio.run(collect())
    asyncio.run(analyse())
    asyncio.run(list_names())

    print(f"[!] {Fore.GREEN}DONE!!{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
