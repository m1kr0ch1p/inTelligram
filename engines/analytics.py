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

# Does analysis by time
async def timeLine(df, ch, dr):
    from pytz import timezone
    from tzlocal import get_localzone

    # Convert the 'Date' column to a datetime object
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y-%m-%d %H:%M:%S%z')

    # Customizing timezone
    try:
        custom_tz = timezone('America/Halifax')
        df['Date'] = df['Date'].dt.tz_localize(custom_tz)
        df['Date'] = df['Date'].dt.tz_convert(custom_tz)
    except Exception as e:
        local_tz = get_localzone()
        df['Date'] = df['Date'].dt.tz_convert(local_tz)

    # Extracting information for the graphs
    df['DayOfWeek'] = df['Date'].dt.day_name()

    # Graph 1: Posts by Hour
    posts_by_hour = df.groupby('Hour').size().reindex(range(24), fill_value=0)    
    plt.figure(figsize=(12, 6))
    posts_by_hour.plot(kind='bar', color='blue') 
    plt.title('Posts by Hour')
    plt.xlabel('Hour of the Day')
    plt.ylabel('Number of Posts')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.grid(axis='y')
    plt.savefig(f'{dr}/{ch}_posts_by_hour.jpg')
    plt.close('all')
    
    # Graph 2: Posts by Day of the Week
    posts_by_day_of_week = df.groupby('DayOfWeek').size()
    posts_by_day_of_week = posts_by_day_of_week.reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    plt.figure(figsize=(12, 6))
    posts_by_day_of_week.plot(kind='bar', color='green')
    plt.title('Posts by Day of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Posts')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{dr}/{ch}_posts_by_day_of_week.jpg')
    plt.close('all')

    # Graph 3: Timeline of All Posts
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values('Date').dropna(subset=['Date']) # Sort DataFrame by date
    plt.plot(df_sorted['Date'], range(1, len(df) + 1), marker='o', linestyle='-', markersize=2)
    #plt.plot(df['Date'], range(len(df)), marker='o', linestyle='-', markersize=2)
    plt.title('Timeline of Posts')
    plt.xlabel('Date')
    plt.ylabel('Number of Posts (Sequential)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{dr}/{ch}_timeline_of_posts.jpg')
    plt.close('all')

# Does NLP analysis
async def get_feelings(df,ch,dr):
    import re
    import wordlist as wl

    feelings_file = open(f'{dr}/{ch}_indicators_speechs.txt', 'a')

    # Defining patterns of words
    for issue_set in wl.target_phrase_sections:
        issue = issue_set[0]
        terms = issue_set[1]

        # Gets messages texts
        for index, row in df.iterrows():
            message = str(row['Text'])
            sentences = message.split()
            author = str(row['Username'])

            for term in terms:
                for sentence in sentences:
                    if term in sentences:
                        output = f'[*] Username {author}:\n - Indicator: {issue}\n - Message: "{message}\n"'
                        feelings_file.write(output)
                        break

# Creates a wordcloud with shared messages
async def word_cloud(df,ch,dr):
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
            final_words = text

    nlp.max_length = 9000000

    doc = nlp(text)

    # gets only nouns and verbs
    final_words = str([token.text for token in doc if token.pos_ in ['NOUN']])

    wc = WordCloud(width = 800, height = 400, background_color = 'white').generate(final_words)

    # Plotting the wordcloud
    plt.figure(figsize = (12, 6))
    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis('off')
    plt.title(f'Channel {ch} content.\n')
    #plt.show()
    cloud_file = f'{dr}/{ch}.png'
    wc.to_file(cloud_file)

# Assigns value to usernames based on messages shared
async def channel_Metrics(df,ch,dr):
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
    for i, (username, count) in enumerate(zip(top_20['Username'][:20], top_20['Quantidade_Mensagens'][:20])):
        ax.text(i, count, f'{username}\n({count})', ha='center', va='bottom', rotation=45)
    
    # Adicionando uma grade horizontal para melhor leitura
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    
    # Ajustando o layout
    plt.tight_layout()
    
    # Storing graph
    plt.savefig(f'{dr}/{ch}_top_users_bar_chart.png')
    plt.close('all')

# Creates usernames list
async def usernames_list(df,ch,dr):
    import csv
    from username_data import get_user_data
    
    # setting csv file
    filename = f'{dr}/usernames_{ch}.csv'
        
    # listing channel users
    unique_usernames = df['Username'].unique()
    sorted_usernames = sorted(map(str, unique_usernames))

    results = []

    for username in sorted_usernames:
        try:
            # obtaining users data
            user_data = await get_user_data(username)
            if user_data:
                results.append(user_data)
            else:
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
    else:
        print('[-] No data to write.')

# Call analysis functions
async def analyse(csv_filename,channel_name_filtered):
    # loads dataframe
    ch = channel_name_filtered
    dr = f'CaseFiles/{ch}'
    chunk_size = 1000

    for df in pd.read_csv(csv_filename, encoding='utf-8', chunksize=chunk_size):
       await word_cloud(df,ch,dr)
       await channel_Metrics(df,ch,dr)
       await timeLine(df,ch,dr)
       await get_feelings(df,ch,dr)
       await usernames_list(df,ch,dr)
