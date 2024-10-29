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

# Creates a wordcloud with shared messages
def word_cloud(df,ch,dr):
    from langdetect import detect # https://pypi.org/project/langdetect/
    from langdetect import DetectorFactory
    import spacy
    from wordcloud import WordCloud

    text = ''.join(map(str, df['Text']))

    # Define a seed
    DetectorFactory.seed = 0
    nlp = None
   
    language = detect(text)
    if language in ['fr', 'en', 'pt', 'es', 'ar']:
        # Load nlp model
        if language == 'fr': # French
            nlp = spacy.load("fr_core_news_sm")
        elif language == 'en': # English
            nlp = spacy.load("en_core_web_sm")
        elif language == 'pt': # portuguese
            nlp = spacy.load("pt_core_news_sm")
        elif language == 'es': # spanish
            nlp = spacy.load("es_core_news_sm")
        elif language == 'ar': # arabian
            nlp = spacy.load("ar_core_news_sm")
        else:
            print('[-] Language not listed.')
            final_words = text

    doc = nlp(text)

    # gets only nouns and verbs
    final_words = str([token.text for token in doc if token.pos_ in ['NOUN', 'VERB']])

    wc = WordCloud(width = 800, height = 400, background_color = 'white').generate(final_words)

    print(f'[+] Drawing wordcloud from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL} messages...')
    # Plotting the wordcloud
    plt.figure(figsize = (12, 6))
    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis('off')
    plt.title(f'Channel {ch} content.\n')
    #plt.show()
    cloud_file = f'{dr}/{ch}.png'
    wc.to_file(cloud_file)


# Assigns value to usernames based on messages shared
def users_Metrics(df,ch,dr):

    print(f'[+] Plotting messages from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
    # Counting messages per usernames
    contagem_usuarios = df.groupby('Username')['Text'].count().reset_index()
    contagem_usuarios.columns = ['Username', 'Quantidade_Mensagens']

    # Creating html bubble graph
    fig = px.scatter(contagem_usuarios, 
                     x='Username', 
                     y='Quantidade_Mensagens', 
                     size='Quantidade_Mensagens', 
                     color='Quantidade_Mensagens',
                     hover_name='Username',
                     #hover_data={'Username': False},  # Oculta o indice no hover
                     title='Messages per Usernames',
                     labels={'Quantidade_Mensagens': 'Numero de Mensagens'},)
                     #size_max=60)

    # Layout personalizing
    fig.update_layout(
        xaxis_title='Usuarios',
        yaxis_title='Numero de Mensagens',
        coloraxis_colorbar_title='Numero de Mensagens'
    )

    # Ajusting axis x banner
    fig.update_xaxes(tickangle=45)

    # Showing the graph
    fig_html_file = f'{dr}/{ch}.html'
    fig.write_html(fig_html_file)
    #fig.show()

    # Creating bar graph

    # Sorting users by the number of messages (descending)
    contagem_usuarios_sorted = contagem_usuarios.sort_values('Quantidade_Mensagens', ascending=False)
    
    # Getting top 20 usernames
    top_20 = contagem_usuarios_sorted.head(20)
    
    # Creating bar graph
    fig, ax = plt.subplots(figsize=(12, 6))
    
    bars = ax.bar(range(len(top_20)), top_20['Quantidade_Mensagens'], align='center')
    
    # Configuring titles and labels
    ax.set_title(f'Top 20 Usernames per messages shared in {ch}')
    ax.set_ylabel('Numbers of messages')
    ax.set_xlabel('Usernames')
    
    # Removing os ticks from axis x
    ax.set_xticks([])
    
    # Adding top 5 names
    for i, (username, count) in enumerate(zip(top_20['Username'][:5], top_20['Quantidade_Mensagens'][:5])):
        ax.text(i, count, f'{username}\n({count})', ha='center', va='bottom')
    
    # Adicionando uma grade horizontal para melhor leitura
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    # Ajustando o layout
    plt.tight_layout()
    
    # Storing graph
    plt.savefig(f'{dr}/{ch}_top_users_bar_chart.png')
    plt.close()


# Creates usernames list
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
    # loads dataframe
    ch = channel_name_filtered
    df = pd.read_csv(csv_filename)
    dr = f'CaseFiles/{ch}'

    # shape
    df.shape

    word_cloud(df,ch,dr)
    users_Metrics(df,ch,dr)
    await usernames_list(df,ch,dr)
