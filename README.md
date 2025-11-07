# inTelligram

## Overview
**inTelligram** is a Python tool inspired by @sockysec [Telerecon](https://github.com/sockysec/Telerecon/tree/main) and designed for scraping Telegram channels to extract content and uploaded files. It facilitates data analysis for intelligence and investigative purposes. 

## Features
- **Content Extraction**: Scrapes messages and files from specified Telegram channels.
- **Data Analysis**: Analyzes extracted data for intelligence purposes.
- **User-Friendly Configuration**: Requires minimal setup through text files.

## Setup Instructions

### Prerequisites
- **Python 3.x**: Ensure that Python is installed on your machine.
- **Required Libraries**: Install necessary libraries using pip.

#### Installation

  ```bash
git clone https://github.com/m1kr0ch1p/inTelligram.git
cd inTelligram
python -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python3 -m spacy download en_core_web_sm
python3 -m spacy download es_core_news_sm
python3 -m spacy download fr_core_news_sm
python3 -m spacy download pt_core_news_sm
python3 -m spacy download ru_core_news_sm
python3 -m spacy download zh_core_web_sm
  ```

You can verify Spacy languages models available here: https://spacy.io/usage/models

### Configuration Files
1. **channels.txt**: Create this file to list the URLs of the Telegram channels you want to scrape. Each URL should be on a new line.
   ```
   https://t.me/channel1
   https://t.me/channel2
   ```

2. **details.py**: This file should include your Telegram API credentials:
   ```python
   API_ID = 'your_api_id'
   API_HASH = 'your_api_hash'
   PHONE_NUMBER = 'your_phone_number'
   ```

## Usage Instructions
To run inTelligram, follow these steps:

1. Open your command line interface (CLI).
2. Navigate to the directory where inTelligram is located.
3. Execute the main script:
   ```bash
   $ python start.py
   ```
### Outputs

- Folder containing downloaded files for metadata investigations
- HTML file with channels Message/Users graph 
- Wordcloud PNG file showing the main terms posted by channels users
- CSV file with channels data scraped (usernames, messases, users ID etc.)
- CSV file with provided users data (username, first and last name, phone number, profile photo in hex string etc.)
- Markdown file with speech indicators analysis based in wordlist set by user
- JPG graphs with channels messages analysis by hours of the day, days of week, timeline etc.
- Markdown file listing metadatas from downloaded files
- Chat sentiment analisys in .txt file

## Contributing
Contributions are welcome! If you find bugs or have suggestions for improvements, please create an issue or submit a pull request on the GitHub repository.

