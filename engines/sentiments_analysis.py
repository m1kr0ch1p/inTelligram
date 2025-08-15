from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from googletrans import Translator
import sys
from colorama import Fore, Style
import pandas as pd
from langdetect import detect, LangDetectException
import asyncio

sys.path.append('engines/')

# Loading list of channels
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Downloads VADER lexicon, needed just once
nltk.download('vader_lexicon', quiet=True)

# Start Vader and translator
sia = SentimentIntensityAnalyzer()
translator = Translator()

async def sentiment_analisys(text, language):

    language = language.lower()
    
    if language == 'en':
        # Analisys from English
        results = sia.polarity_scores(text)
    elif language == 'unknown':
        print(f'[-] It was not possible identify the language in {text}')
    else: 
        # Translate text to English
        translation = await translator.translate(text, src=language, dest='en')
        translated_text = translation.text
        # Analisa o text traduzido
        results = sia.polarity_scores(translated_text)
    #else:
    #    raise ValueError(f"Language '{language}' not suported. Use 'en', 'es', 'pt' ou 'fr'.")
    
        return results

def detect_language(text):
    if not text or text.strip() == "":
        return 'unknown'  # Empty text or spaces
    try:
        lang = detect(text)
        return lang
    except LangDetectException:
        return 'unknown'  # Not possible detect language

# main function
async def sentiment():

    channel_list = load_channel_list()

    # Todo: COMMENT HERE
    for channel_name in channel_list:
        try:
            ch = channel_name.rsplit("/",1)[-1]
            print(f'[+] Analyzing sentiments from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
            dr = f'CaseFiles/{ch}'
            csv_filename = f'{dr}/{ch}.csv'
            df = pd.read_csv(csv_filename, encoding='utf-8')
            output_file = open(f'{dr}/{ch}_sentiment_analisys.txt', 'a', encoding='utf-8')

            for _, row in df.iterrows():
                text = str(row['Text'])
                author = str(row['Username'])
                if text == 'nan':
                    pass
                else:
                    language = detect_language(text)

                    sentiment = await sentiment_analisys(text, language)
                    print(f"[+] Language: {language} | {Fore.GREEN}Author:{Style.RESET_ALL} {author} | {Fore.YELLOW}Scores:{Style.RESET_ALL} {sentiment}\n{text}\n\n")
                    output_file.write(f"[+] Language: {language} | {Fore.GREEN}Author:{Style.RESET_ALL} {author} | {Fore.YELLOW}Scores:{Style.RESET_ALL} {sentiment}\n{text}\n\n")
                    
            output_file.close()
                    
        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []
