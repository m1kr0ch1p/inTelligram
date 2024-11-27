#from engine import collect
import asyncio
from colorama import Fore, Style

# https://docs.telethon.dev/en/stable/

# Banner
def banner():
    banner = f"""{Fore.RED}
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

# Calling local functions
banner()
ip_check()
ignite()
# Calling data collector
exec(open("engines/engine.py").read())
