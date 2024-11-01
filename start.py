#from engine import collect
import asyncio
from colorama import Fore, Style

# https://docs.telethon.dev/en/stable/

api_id = None
api_hash = None
phone_number = None

# Function to update details.py file
def update_details_file(api_id, api_hash, phone_number):
    with open("details.py", "w") as file:
        file.write(f'apiID = "{api_id}"\n')
        file.write(f'apiHash = "{api_hash}"\n')
        file.write(f'number = "{phone_number}"\n')

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

#init(autoreset=True)
def check_details_file():
    while True:
        try:
            api_id = input("Please enter your API ID:\n")
            print(f'You entered "{api_id}"')
            confirmation = input('Is this correct? (y/n)')
            if confirmation.lower() == 'y':
                print('Updating...')
                break
        except:
            continue
    
    while True:
        try:
            api_hash = input("Please enter your API Hash:\n")
            print(f'You entered "{api_hash}"')
            confirmation = input('Is this correct? (y/n)')
            if confirmation.lower() == 'y':
                print('Updating...')
                break
        except:
            continue
    
    while True:
        try:
            phone_number = input("Please enter your phone number:\n")
            print(f'You entered "{phone_number}"')
            confirmation = input('Is this correct? (y/n)')
            if confirmation.lower() == 'y':
                print('Updating...')
                break
        except:
            continue
    
    update_details_file(api_id, api_hash, phone_number)
    
    print('Setup is complete.')

# receive channels to collect and analyse
def ignite():
    global channel_list
    channel_list = []
    channel_file = 'engines/channels.txt'
    with open(channel_file, "r") as file:
        for channel in file:
            channel_list.append(channel.strip())
    #print(channel_list)

# Calling local functions
ip_check()
#check_details_file()
ignite()
# Calling data collector
exec(open("engines/engine.py").read())
