import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import os
import sys
import asyncio
from colorama import Fore, Style
from pytz import timezone
from tzlocal import get_localzone
from langdetect import detect, DetectorFactory
import spacy
from wordcloud import WordCloud
import traceback
import psutil

sys.path.append('engines/')
matplotlib.use('Agg')

# Loading list of channels
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Draw messages timeline from channel
def timeLine(df, ch, dr):
    # Converting dates and fixing time zone
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y-%m-%d %H:%M:%S%z')
    df = df.dropna(subset=['Date'])  # Deleting invalid dates

    local_tz = get_localzone()
    df['Date'] = df['Date'].dt.tz_convert(local_tz)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Hour'] = df['Date'].dt.hour

    # Plotting posts by hour
    posts_by_hour = df['Hour'].value_counts().reindex(range(24), fill_value=0).sort_index()
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

    # Plotting posts by days of week
    posts_by_day_of_week = df['DayOfWeek'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0)
    plt.figure(figsize=(12, 6))
    posts_by_day_of_week.plot(kind='bar', color='green')
    plt.title('Posts by Day of the Week')
    plt.xlabel('Day of the Week')
    plt.ylabel('Number of Posts')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{dr}/{ch}_posts_by_day_of_week.jpg')
    plt.close('all')

    # Plotting posts timeline
    plt.figure(figsize=(12, 6))
    df_sorted = df.sort_values('Date')
    plt.plot(df_sorted['Date'], range(1, len(df_sorted) + 1), marker='o', linestyle='-', markersize=2)
    plt.title('Timeline of Posts')
    plt.xlabel('Date')
    plt.ylabel('Number of Posts (Sequential)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{dr}/{ch}_timeline_of_posts.jpg')
    plt.close('all')

# Makes speech analysis
async def get_indicators(df, ch, dr):
    import wordlist as wl

    feelings_file = open(f'{dr}/{ch}_indicators_speechs.txt', 'a')
    for issue_set in wl.target_phrase_sections:
        issue = issue_set[0]
        terms = issue_set[1]

        for _, row in df.iterrows():
            message = str(row['Text'])
            author = str(row['Username'])

            for term in terms:
                if term in message.split():
                    output = f'[*] Username {author}:\n - Indicator: {issue}\n - Message: "{message}"\n'
                    feelings_file.write(output)
                    break

async def word_cloud(df, ch, dr):
    text = ''.join(map(str, df['Text']))
    DetectorFactory.seed = 0

    language = detect(text)
    lang_model_map = {
        'fr': 'fr_core_news_sm',
        'en': 'en_core_web_sm',
        'pt': 'pt_core_news_sm',
        'es': 'es_core_web_sm',
        'ar': 'ar_core_news_sm'
    }

    if language in lang_model_map:
        nlp = spacy.load(lang_model_map[language])
    else:
        nlp = None

    final_words = []

    if nlp:
        chunk_size = 100000  # Tamanho do bloco de texto a ser processado por vez
        nlp.max_length = chunk_size + 10000  # Ajusta o limite máximo do spaCy para o tamanho do bloco

        for i in range(0, len(text), chunk_size):
            chunk = text[i:i+chunk_size]
            doc = nlp(chunk)
            final_words.extend([token.text for token in doc if token.pos_ == 'NOUN'])
        
        final_words = ' '.join(final_words)
    else:
        final_words = text

    wc = WordCloud(width=800, height=400, background_color='white').generate(final_words)
    plt.figure(figsize=(12, 6))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title(f'Channel {ch} content.\n')
    wc.to_file(f'{dr}/{ch}_word_cloud.png')

async def channel_Metrics(df, ch, dr):
    contagem_usuarios = df.groupby('Username')['Text'].count().reset_index()
    contagem_usuarios.columns = ['Username', 'Quantidade_Mensagens']

    fig = px.scatter(contagem_usuarios, x='Username', y='Quantidade_Mensagens', size='Quantidade_Mensagens', color='Quantidade_Mensagens', hover_name='Username', title='Messages per Usernames', labels={'Quantidade_Mensagens': 'Número de Mensagens'})
    fig.update_layout(xaxis_title='Usuários', yaxis_title='Número de Mensagens', coloraxis_colorbar_title='Número de Mensagens')
    fig.update_xaxes(tickangle=45)
    fig.write_html(f'{dr}/{ch}.html')

    top_20 = contagem_usuarios.sort_values('Quantidade_Mensagens', ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(top_20)), top_20['Quantidade_Mensagens'], align='center')
    ax.set_title(f'Top 20 Usernames per messages shared in {ch}')
    ax.set_ylabel('Números de mensagens')
    ax.set_xlabel('Usernames')
    ax.set_xticks([])
    for i, (username, count) in enumerate(zip(top_20['Username'][:20], top_20['Quantidade_Mensagens'][:20])):
        ax.text(i, count, f'{username}\n({count})', ha='center', va='bottom', rotation=45)
    ax.yaxis.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(f'{dr}/{ch}_top_users_bar_chart.png')
    plt.close('all')

async def channel_engagement(df, ch, dr):

    plot=True

    # Count messages per user
    messages_per_user = df['Username'].value_counts()
    
    # Calculate engagement metrics
    total_users = len(messages_per_user)
    total_messages = messages_per_user.sum()
    mean_messages = total_messages / total_users
    median_messages = messages_per_user.median()
    
    # Gini coefficient calculation
    def gini(x):
        mad = np.abs(np.subtract.outer(x, x)).mean()
        rmad = mad/np.mean(x)
        g = 0.5 * rmad
        return g
    
    gini_coefficient = gini(messages_per_user.values)
    
    # Participation percentiles
    percentiles = messages_per_user.quantile([0.25, 0.5, 0.75, 0.9])
    
    # Lorenz curve function
    def lorenz_curve(x):
        x_lorenz = x.cumsum() / x.sum()
        x_lorenz = np.insert(x_lorenz, 0, 0)
        y_lorenz = np.arange(x_lorenz.size) / (x.size)
        return x_lorenz, y_lorenz
    
    # Optional plotting
    if plot:
        # Messages distribution histogram
        plt.figure(figsize=(10, 6))
        plt.hist(messages_per_user, bins=50, edgecolor='black')
        #messages_per_user.hist(bins=50)
        plt.title('Message Distribution per User')
        plt.xlabel('Number of Messages')
        plt.ylabel('Number of Users')
        plt.savefig(f'{dr}/{ch}_messages_distribution.png')
        plt.close('all')
        
        # Lorenz curve
        x_lorenz, y_lorenz = lorenz_curve(np.sort(messages_per_user.values))
        plt.figure(figsize=(10, 6))
        plt.plot(y_lorenz, x_lorenz, label='Lorenz Curve')
        plt.plot([0, 1], [0, 1], 'r--', label='Perfect Equality Line')
        plt.title('Lorenz Curve - Message Distribution')
        plt.xlabel('Cumulative Proportion of Users')
        plt.ylabel('Cumulative Proportion of Messages')
        plt.legend()
        plt.savefig(f'{dr}/{ch}_lorenz_curve.png')
        plt.close('all')

    # Prepare results dictionary
    results = {
        'total_users': total_users,
        'total_messages': total_messages,
        'gini_coefficient': gini_coefficient,
        'mean_messages_per_user': mean_messages,
        'median_messages_per_user': median_messages,
        'participation_percentiles': percentiles.to_dict()
    }

    # Print results
    print("Channel Engagement Analysis:")
    for key, value in results.items():
        print(f"{key}: {value}")
    
    return results
    
# Call analysis functions
async def analyse():

    channel_list = load_channel_list()

    for channel_name in channel_list:
        ch = channel_name.rsplit("/",1)[-1]
        print(f'[+] Analyzing data from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
        dr = f'CaseFiles/{ch}'
        csv_filename = f'{dr}/{ch}.csv'
        df = pd.read_csv(csv_filename, encoding='utf-8')
        try:
            await word_cloud(df,ch,dr)
            await channel_Metrics(df,ch,dr)
            timeLine(df,ch,dr)
            await get_indicators(df,ch,dr)
            await channel_engagement(df,ch,dr)
        except FileNotFoundError:
            print(f"[-] There is no CSV file in {dr}")
        except Exception as e:
            print(f"[-] Error: {e}")

asyncio.run(analyse())
print(f"[!] {Fore.GREEN}DONE!!{Style.RESET_ALL}")
