from setuptools import setup, find_packages
import subprocess

def download_corpora():
    subprocess.call(['python3', '-m', 'textblob.download_corpora'])
    subprocess.call(['python', '-m', 'spacy', 'download', 'pt_core_news_sm'])
    subprocess.call(['python', '-m', 'spacy', 'download', 'en_core_web_sm'])
    subprocess.call(['python', '-m', 'spacy', 'download', 'fr_core_news_sm'])
    subprocess.call(['python', '-m', 'spacy', 'download', 'es_core_news_sm'])
    subprocess.call(['python', '-m', 'spacy', 'download', 'ar_core_news_sm'])

setup(
    name='seu_projeto',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'jsonlib',
        'colorama',
        'asyncio',
        'pandas',
        'telethon',
        'plotly',
        'matplotlib',
        'numpy',
        'wordcloud',
        'datetime',
        'pillow',
        'textblob==0.15.3',
        'certifi',
        'langdetect',
        'spacy',
        'pytz',
        'nltk',
        'tzlocal'
    ],
    cmdclass={
        'download_corpora': download_corpora,
    },
)
