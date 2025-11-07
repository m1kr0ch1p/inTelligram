import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import sys
from colorama import Fore, Style
from pytz import timezone
from tzlocal import get_localzone
from langdetect import detect
import spacy
from wordcloud import WordCloud, STOPWORDS
from collections import Counter

sys.path.append('engines/')
matplotlib.use('Agg')

# Loading list of channels
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r", encoding='utf-8') as file:
        return [line.strip() for line in file]

# Draw messages timeline from channel
def timeLine(df, ch, dr):
    try:
        # Converting dates and fixing time zone
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y-%m-%d %H:%M:%S%z')
        df = df.dropna(subset=['Date'])  # Deleting invalid dates

        local_tz = get_localzone()
        df['Date'] = df['Date'].dt.tz_convert(local_tz)
        df['DayOfWeek'] = df['Date'].dt.day_name()
        df['Hour'] = df['Date'].dt.hour
        
        # Plotting messages by hour
        posts_by_hour = df['Hour'].value_counts().reindex(range(24), fill_value=0).sort_index()
        plt.figure(figsize=(12, 6))
        posts_by_hour.plot(kind='bar', color='blue')
        plt.title('Messages/Hour')
        plt.xlabel('Hours/Day')
        plt.ylabel('Number of Messages')
        plt.xticks(rotation=0)
        plt.tight_layout()
        plt.grid(axis='y')
        plt.savefig(f'{dr}/{ch}_messages_by_hour.jpg')
        plt.close('all')

        # Plotting messages by days of week
        posts_by_day_of_week = df['DayOfWeek'].value_counts().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'], fill_value=0)
        plt.figure(figsize=(12, 6))
        posts_by_day_of_week.plot(kind='bar', color='green')
        plt.title('Messages/Days of the Week')
        plt.xlabel('Days of the Week')
        plt.ylabel('Number of Messages')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{dr}/{ch}_messages_by_day_of_week.jpg')
        plt.close('all')
        
        # Plotting posts timeline
        plt.figure(figsize=(12, 8), dpi=600)
        #df_sorted = df.sort_values('Date')
        #plt.plot(df_sorted['Date'], range(1, len(df_sorted) + 1), marker='o', linestyle='-', markersize=2)

        df_counts = df.groupby('Date').size().reset_index(name='MessageCount')
        df_counts = df_counts.sort_values('Date')
        counts = df.groupby(df['Date'].dt.date).size()

        plt.figure(figsize=(10,5))
        counts.plot(kind='line')
        plt.title('Messages Timeline')
        plt.xlabel('Date')
        plt.ylabel('Messages')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(f'{dr}/{ch}_timeline_of_messages.jpg')
        plt.close('all')

    except Exception as e:
        print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
        return []
    
# Makes speech analysis
async def get_indicators(df, ch, dr):
    import wordlist as wl

    feelings_file = open(f'{dr}/{ch}_indicators_speechs.md', 'a', encoding='utf-8')
    try:
        for issue_set in wl.target_phrase_sections:
            issue = issue_set[0]
            terms = issue_set[1]

            for _, row in df.iterrows():
                message = str(row['Text'])
                author = str(row['Username'])

                for term in terms:
                    if term in message.split():
                        output = f'## Username {author}:\n\n - Indicator: {issue}\n - Message: \n```\n"{message}"\n```\n\n'
                        feelings_file.write(output)
                        break
    except Exception as e:
        print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
        return []

# Create wordcloud
async def word_cloud(df, ch, dr):
    text = ''.join(map(str, df['Text'])).lower()

    #DetectorFactory.seed = 0

    language = detect(text)
    lang_model_map = {
        'fr': 'fr_core_news_sm',
        'en': 'en_core_web_sm',
        'pt': 'pt_core_news_sm',
        'es': 'es_core_news_sm',
        'ru': 'ru_core_news_sm',
        'zh': 'zh_core_web_sm'
    }
    try:
        if language in lang_model_map:
            nlp = spacy.load(lang_model_map[language])
        else:
            nlp = None

        final_words = []

        if nlp:
            chunk_size = 100000  # Text block lenght processed by turn
            nlp.max_length = chunk_size + 10000  # Fix spaCy max limint to block lenght

            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                doc = nlp(chunk)
                final_words.extend([token.text for token in doc if token.pos_ == 'NOUN'])

            final_words = ' '.join(final_words)
        else:
            final_words = text

        stopWords = set(STOPWORDS)
        stopWords.update(["a", "à", "ao", "aos", "aquela", "aquele", "aqueles", "aquilo", "as", 
                          "até", "com", "como", "da", "das", "de", "dela", "dele", "deles", "depois", 
                          "do", "dos", "e", "ela", "ele", "eles", "em", "entre", "era", "eram", "essa", 
                          "esse", "esses", "esta", "está", "estamos", "estão", "eu", "faz", "foi", "foram", 
                          "há", "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo", "muito", 
                          "na", "nas", "nem", "no", "nos", "nós", "o", "os", "ou", "para", "pela", "pelas", 
                          "pelo", "pelos", "por", "qual", "quando", "que", "se", "ser", "seu", "sua", "te", 
                          "tem", "tendo", "ter", "teu", "tu", "um", "uma", "vós", "vamos", "vão", "você", 
                          "vocês", "al", "algo", "algunas", "algunos", "ante", "antes", "como", "con", "contra", 
                          "cual", "cuando", "de", "del", "desde", "donde", "durante", "e", "el", "ella", "ellos", 
                          "en", "entre", "era", "eran", "es", "esa", "ese", "eso", "esta", "está", "estamos", 
                          "están", "estoy", "fue", "han", "la", "las", "le", "lo", "los", "más", "me", "mi", "mis", 
                          "muy", "ningún", "no", "nos", "o", "para", "pero", "por", "qué", "se", "ser", "si", 
                          "sin", "sobre", "son", "su", "sus", "también", "tan", "tanto", "te", "tu", "tus", "un", 
                          "una", "unos", "yo", "au", "aux", "avec", "ce", "ces", "dans", "de", "des", "du", "elle", 
                          "en", "et", "eux", "il", "je", "la", "le", "leur", "lui", "ma", "mais", "me", "même", 
                          "mes", "moi", "mon", "ne", "nos", "notre", "nous", "on", "ou", "par", "pas", "pour", 
                          "qu", "que", "qui", "sa", "se", "ses", "son", "sur", "ta", "te", "tes", "toi", "ton", 
                          "tu", "un", "une", "vos", "votre", "vous", "c", "d", "j", "l", "m", "n", "s", "t", 
                          "y", "été", "étée", "étées", "étés", "étant", "suis", "es", "est", "sommes", "êtes", 
                          "sont", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", 
                          "are", "aren't", "as", "at", "be", "because", "been", "before", "being", "below", 
                          "between", "both", "but", "by", "can't", "cannot", "could", "couldn't", "did", "didn't", 
                          "do", "does", "doesn't", "doing", "don't", "down", "during", "each", "few", "for", "from", 
                          "further", "had", "hadn't", "has", "hasn't", "have", "haven't", "having", "he", "he'd", 
                          "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself", "his", "how", 
                          "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's", 
                          "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself", "no", "nor", 
                          "not", "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", 
                          "ourselves", "out", "over", "own", "same", "shan't", "she", "she'd", "she'll", "she's", 
                          "should", "shouldn't", "so", "some", "such", "than", "that", "that's", "the", "their", 
                          "theirs", "them", "themselves", "then", "there", "there's", "these", "they", "they'd", 
                          "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under", "until", 
                          "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", 
                          "what", "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", 
                          "whom", "why", "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", 
                          "you're", "you've", "your", "yours", "yourself", "yourselves"])

        wc = WordCloud(width=800, height=400, background_color='white', max_words=50, stopwords=stopWords).generate(final_words)
        plt.figure(figsize=(12, 6))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Channel {ch} most used words.\n')
        wc.to_file(f'{dr}/{ch}_word_cloud.jpg')
        plt.close('all')

    except Exception as e:
        print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
        return []

# All channel metrics
async def channel_Metrics(df, ch, dr):
    users_count = df.groupby('Username')['Text'].count().reset_index()
    users_count.columns = ['Username', 'messages_count']
    messages_per_user = df['Username'].value_counts().reset_index()
    messages_per_user.columns = ['Username', 'MessageCount']  

    try:
        ## 20 Most active usernames (HTML)
        fig = px.scatter(users_count, x='Username', y='messages_count', size='messages_count', color='messages_count', hover_name='Username', title='Messages per Usernames', labels={'messages_count': 'Number of messages'})
        fig.update_layout(xaxis_title='Users', yaxis_title='Number of messages', coloraxis_colorbar_title='Number of messages')
        fig.update_xaxes(tickangle=45)
        fig.write_html(f'{dr}/{ch}.html')

        ## Dispersion graph
        plt.scatter(messages_per_user['Username'], messages_per_user['MessageCount'])
        plt.xlabel('Users')
        plt.ylabel('Messages')
        plt.title('Dispersion: Users x Messages')
        plt.xticks([])
        plt.savefig(f'{dr}/{ch}_dispersion_graph.jpg')
        plt.close('all')

        ## 20 Most active usernames (JPG)
        top_20 = users_count.sort_values('messages_count', ascending=False).head(20)
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(range(len(top_20)), top_20['messages_count'], align='center')
        ax.set_title(f'Top 20 Usernames per messages shared in {ch}')
        ax.set_ylabel('Number of messages')
        ax.set_xlabel('Usernames')
        ax.set_xticks([])
        for i, (username, count) in enumerate(zip(top_20['Username'][:20], top_20['messages_count'][:20])):
            ax.text(i, count, f'{username}\n({count})', ha='center', va='bottom', rotation=45)
        ax.yaxis.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'{dr}/{ch}_top_users_bar_chart.jpg')
        plt.close('all')

    except Exception as e:
        print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
        return []

async def channel_engagement(df, ch, dr):

    plot=True

    # Count messages per user
    messages_per_user = df['Username'].value_counts()
    
    try:

        ## Calculates engagement metrics
        total_users = len(messages_per_user)
        total_messages = messages_per_user.sum()
        mean_messages = total_messages / total_users
        median_messages = messages_per_user.median()

        ## Gini coefficient calculation
        def gini(x):
            try:
                mad = np.abs(np.subtract.outer(x, x)).mean()
                rmad = mad/np.mean(x)
                g = 0.5 * rmad
                return g
            except Exception as e:
                print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
                return []
    
        gini_coefficient = gini(messages_per_user.values)

    except Exception as e:
        print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
        return []

    ## Participation percentiles
    percentiles = messages_per_user.quantile([0.25, 0.5, 0.75, 0.9])
    
    ## Lorenz curve function
    def lorenz_curve(x):
        try:
            x_lorenz = x.cumsum() / x.sum()
            x_lorenz = np.insert(x_lorenz, 0, 0)
            y_lorenz = np.arange(x_lorenz.size) / (x.size)
            return x_lorenz, y_lorenz
    
        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []
    
    # Optional plotting
    if plot:
        try:
            ## Messages distribution histogram
            plt.figure(figsize=(10, 6))
            plt.hist(messages_per_user, bins=50, color='blue')
            plt.title('Messages per Users')
            plt.xlabel('Number of messages')
            plt.ylabel('Number of users')
            plt.savefig(f'{dr}/{ch}_messages_distribution.jpg')
            plt.close('all')

            ## Lorenz curve
            x_lorenz, y_lorenz = lorenz_curve(np.sort(messages_per_user.values))
            plt.figure(figsize=(10, 6))
            plt.plot(y_lorenz, x_lorenz, label='Lorenz Curve')
            plt.plot([0, 1], [0, 1], 'r--', label='Perfect Equality Line')
            plt.title('Lorenz Curve - Message Distribution')
            plt.xlabel('Cumulative Proportion of Users')
            plt.ylabel('Cumulative Proportion of Messages')
            plt.legend()
            plt.savefig(f'{dr}/{ch}_lorenz_curve.jpg')
            plt.close('all')

        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []

    # Prepare results dictionary
    results = {
        'Total of users': total_users,
        'Total of messages': total_messages,
        'Gini coefficient (messages distribution)': gini_coefficient,
        'Mean of messages per user': mean_messages,
        'Median messages per user': median_messages,
        'Participation percentiles': percentiles.to_dict()
    }

    # Print results
    print("Channel Engagement Analysis:")
    for key, value in results.items():
        print(f"{key}: {value}")
    
    return results
    
# Call analysis functions
async def analyse():

    channel_list = load_channel_list()

    # Todo: COMMENT HERE
    for channel_name in channel_list:
        try:
            ch = channel_name.rsplit("/",1)[-1]
            print(f'[+] Analyzing data from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
            dr = f'CaseFiles/{ch}'
            csv_filename = f'{dr}/{ch}.csv'
            df = pd.read_csv(csv_filename, encoding='utf-8')
        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []

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

