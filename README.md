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
- **Required Libraries**: Install necessary libraries using pip:
  ```bash
  $ python install -r requirements.txt
  $ python -m pip install setup.py
  ```

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
- TXT file with speech indicators analysis based in wordlist
- JPG graphs with channels messages analysis by hours of the day, days of week, timeline etc.

## Contributing
Contributions are welcome! If you find bugs or have suggestions for improvements, please create an issue or submit a pull request on the GitHub repository.

