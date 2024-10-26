#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import os
from colorama import Fore, Style

# Handling ICE default IO error handle due to x11
matplotlib.use('Agg')

# cria nuvem de palavras com os textos compartilhados
def word_cloud(df,ch,dr):
    from wordcloud import WordCloud

    texto = ''.join(map(str, df['Text']))

    wc = WordCloud(width = 800, height = 400, background_color = 'white').generate(texto)

    print(f'[+] Drawing wordcloud from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL} messages...')
    # Plot da nuvem de palavra
    plt.figure(figsize = (12, 6))
    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis('off')
    plt.title(f'Conteudo de texto do Grupo {ch}\n')
    #plt.show()
    cloud_file = f'{dr}/{ch}.png'
    wc.to_file(cloud_file)

# atribui valor aos usernames de acordo com mensagens postadas
def users_Metrics(df,ch,dr):

    print(f'[+] Plotting messages from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
    # Contando o numero de mensagens por usuario
    contagem_usuarios = df.groupby('Username')['Text'].count().reset_index()
    contagem_usuarios.columns = ['Username', 'Quantidade_Mensagens']

    # Criando o grafico de bolhas
    fig = px.scatter(contagem_usuarios, 
                     x='Username', 
                     y='Quantidade_Mensagens', 
                     size='Quantidade_Mensagens', 
                     color='Quantidade_Mensagens',
                     hover_name='Username',
                     #hover_data={'Username': False},  # Oculta o indice no hover
                     title='Quantidade de Mensagens por Usuario',
                     labels={'Quantidade_Mensagens': 'Numero de Mensagens'},)
                     #size_max=60)

    # Personalizando o layout
    fig.update_layout(
        xaxis_title='Usuarios',
        yaxis_title='Numero de Mensagens',
        coloraxis_colorbar_title='Numero de Mensagens'
    )

    # Ajustando a posicao dos rotulos no eixo x
    fig.update_xaxes(tickangle=45)

    # Exibindo o grafico
    fig_html_file = f'{dr}/{ch}.html'
    fig.write_html(fig_html_file)
    #fig.show()

# cria lista de Usernames

async def usernames_list(df,ch,dr):
    import csv
    from username_data import get_user_data
    
    # setting csv file
    filename = f'{dr}/usernames_{ch}.csv'

    print(f'[*] Extractinig users data from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
        
    # listing channel users
    unique_usernames = df['Username'].unique()
    sorted_usernames = sorted(map(str, unique_usernames))

    results = []

    for username in sorted_usernames:
        try:
            # obtaining users data
            user_data = await get_user_data(username)

            if user_data:
                print(f'[+] Username: {username} -> OK')
                results.append(user_data)
            else:
                print(f'[-] No data found for user {username}')
                continue

        except Exception as e:
            continue

    if results:
        with open(filename, mode='w', encoding='utf-8', newline='') as file:
            fieldnames = results[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for row in results:
                writer.writerow(row)
        print(f'Usernames from {ch} are stored in {filename}.\n')
    else:
        print(f'[-] No data to write for {ch}.\n')


# Call analysis functions
async def analyse(csv_filename,channel_name_filtered):
    # carrega o dataframe
    ch = channel_name_filtered
    df = pd.read_csv(csv_filename)
    dr = f'CaseFiles/{ch}'

    # shape
    df.shape

    word_cloud(df,ch,dr)
    users_Metrics(df,ch,dr)
    await usernames_list(df,ch,dr)
