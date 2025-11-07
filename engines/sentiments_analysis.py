from colorama import Fore, Style
import asyncio
import pandas as pd
from langdetect import detect, LangDetectException
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from googletrans import Translator  # type: ignore
import matplotlib.pyplot as plt

# Baixar lexicon do VADER (se ainda não tiver)
nltk.download('vader_lexicon', quiet=True)

# Inicializar VADER e tradutor
sia = SentimentIntensityAnalyzer()
translator = Translator()

import sys
sys.path.append('engines/')

def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]


def detect_language(text):
    try:
        return detect(text)
    except LangDetectException:
        return 'unknown'

async def analyze_sentiment(text, language):
    language = language.lower()
    try:
        if language == 'en':
            scores = sia.polarity_scores(text)
        elif language == 'unknown':
            scores = {'compound': 0.0}  # Sentimento neutro para desconhecido
        else:
            translated = await translator.translate(text, src=language, dest='en')
            scores = sia.polarity_scores(translated.text)
        return scores
    except Exception:
        return {'compound': 0.0}

def classify_sentiment(compound_score):
    if compound_score > 0.05:
        return 'Positive'
    elif compound_score < -0.05:
        return 'Negative'
    else:
        return 'Neutral'

async def sentiment():
    channel_list = load_channel_list()

    for channel_name in channel_list:

        ch = channel_name.rsplit("/", 1)[-1]
        print(f'[+] Analyzing sentiments from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
        dr = f'CaseFiles/{ch}'
        csv_filename = f'{dr}/{ch}.csv'
        df = pd.read_csv(csv_filename, encoding='utf-8')

        async def process_text(text):
            lang = detect_language(text)
            scores = await analyze_sentiment(text, lang)
            classification = classify_sentiment(scores['compound'])
            return classification

        async def gather_classifications(df):
            texts = df['Text'].dropna().tolist()
            tasks = [process_text(text) for text in texts]
            sentiments = await asyncio.gather(*tasks)
            return sentiments

        sentiments =  await gather_classifications(df)

        # Contagem dos sentimentos
        counts = pd.Series(sentiments).value_counts().reindex(['Positive', 'Negative', 'Neutral'], fill_value=0)

        # Gráfico de pizza
        plt.figure(figsize=(8, 8))
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['green', 'red', 'gray'], startangle=140)
        plt.title('Distribuição de Sentimentos (Gráfico de Pizza)')
        plt.savefig(f'{dr}/{ch}_sentiments_piechart.jpg')

        # Gráfico de barras
        plt.figure(figsize=(8, 6))
        counts.plot(kind='bar', color=['green', 'red', 'gray'])
        plt.title('Distribuição de Sentimentos (Gráfico de Barras)')
        plt.ylabel('Número de Mensagens')
        plt.xticks(rotation=0)
        plt.savefig(f'{dr}/{ch}_sentiments_bar.jpg')
