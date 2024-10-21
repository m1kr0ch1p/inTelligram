from colorama import init, Fore, Style
from engine import collect
import asyncio

# Funcao para criar/atualizar o arquivo details.py
def update_details_file(api_id, api_hash, phone_number):
    with open("details.py", "w") as file:
        file.write(f'apiID = "{api_id}"\n')
        file.write(f'apiHash = "{api_hash}"\n')
        file.write(f'number = "{phone_number}"\n')

# Define os detalhes do usuario
# OBS: A seguranca das credenciais pode ser otimizada se utilizar input para
#      as variaveis.


def ip_check():
    import json
    import requests

    try:
        webURL = 'http://ip-api.com/json/?fields=61439'
        json_data = requests.get(webURL).json()

        # Dumpando e Carregando o JSON
        dataB = json.dumps(json_data)
        data = json.loads(dataB)

        # Extraindo informações
        country_code = data['countryCode']
        city = data['city']
        query = data['query']

        # Formato
        formatted_info = f"{city}-{country_code} (IP Adress {query})"

        # Imprimindo o resultado
        print(f'[*] You are connected to Internet from {Fore.YELLOW}{formatted_info}{Style.RESET_ALL}\n')
    except erro as e:
        print(f'{Fore.RED}[-] {e}{Style.RESET_ALL}')

#init(autoreset=True)

api_id = ''
api_hash = ''
phone_number = ''

# Atualiza o arquivo details e executa a funca collect de engine

update_details_file(api_id, api_hash, phone_number)
ip_check()
asyncio.run(collect())
