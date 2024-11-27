#!/bin/bash

pip install colorama asyncio pandas telethon plotly matplotlib numpy==1.26.4 wordcloud datetime pillow textblob==0.15.3 certifi langdetect pytz nltk tzlocal corpora
pip install -U pip setuptools wheel
pip install spacy
python -m spacy download en_core_web_sm
python -m spacy download fr_core_news_sm
python -m spacy download es_core_news_sm
python -m spacy download pt_core_news_sm
#python -m spacy download ar_core_news_sm
