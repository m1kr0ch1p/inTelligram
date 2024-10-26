from colorama import Fore, Style

# Inspired in https://docs.telethon.dev/en/stable/

api_id = None
api_hash = None
phone_number = None

# receive channels to collect and analyse
def ignite():
    global channel_list
    channel_list = []
    channel_file = 'channels.txt'
    with open(channel_file, "r") as file:
        for channel in file:
            channel_list.append(channel.strip())
    #print(channel_list)

# Calling local functions
ip_check()
ignite()
# Calling data collector
exec(open("engine.py").read())
