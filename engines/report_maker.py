import sys
from colorama import Fore, Style
import os
import asyncio
sys.path.append('engines/')

# Loading list of channels
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r", encoding='utf-8') as file:
        return [line.strip() for line in file]


async def report():
    channel_list = load_channel_list()

    # Todo: COMMENT HERE
    for channel_name in channel_list:
        try:
            ch = channel_name.rsplit("/",1)[-1]
            print(f'[+] Creating report to {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...')
            dr = f'CaseFiles/{ch}'
            report_filename = f'{dr}/{ch}-Report.md'
            report = open(report_filename, 'a', encoding='utf-8')

           # Start Report writting
            report.write(f'# REPORT - CASE: {channel_name}'+'\n'*5)
            report.write(f'## 1. Introduction\n You can edit this topic here.\n\n')
            report.write(f'## 2. Executive Summary\n You can edit this topic here.\n\n')
            report.write(f'## 3. Findigs\n You can edit this topic here.\n\n')

            # Adding images to Report (from Analisys)
            report.write(f'### 3.1. Chat\'s Behaviours\n\n\n')
            report.write(f'TEXT HERE ABOUT TIMELINE OF MESSAGES\n\n')
            report.write(f'![{ch} timeline of messages]({ch}_timeline_of_messages.jpg)\n\n\n')
            report.write(f'TEXT HERE ABOUT FREQUENCY OF MESSAGES\n\n')
            report.write(f'![{ch} weekly frequency of messages]({ch}_messages_by_day_of_week.jpg)\n\n\n')
            report.write(f'TEXT HERE ABOUT FREQUENCY OF MESSAGES\n\n')
            report.write(f'![{ch} daily frequency of messages]({ch}_messages_by_hour.jpg)\n\n\n')
            report.write(f'TEXT HERE ABOUT FREQUENCY OF TERMS\n\n')
            report.write(f'![{ch} frequency of words]({ch}_word_cloud.jpg)\n\n\n')
            report.write(f'#### 3.1.1. Users\' behavious\n\n\n')
            report.write(f'TEXT HERE ABOUT FREQUENCY OF USERS MESSAGES\n\n')
            report.write(f'![{ch} most frequent users by messages]({ch}_top_users_bar_chart.jpg)\n\n\n')
            report.write(f'TEXT HERE ABOUT FREQUENCY OF USERS/MESSAGES DISTRIBUTION\n\n')
            report.write(f'![{ch} Users per messages distribution]({ch}_messages_distribution.jpg)\n\n\n')
            report.write(f'TEXT HERE ABOUT FREQUENCY OF MESSAGES/USERS DISTRIBUTION\n\n')
            report.write(f'![{ch} Messages per users distribution]({ch}_lorenz_curve.jpg)\n\n\n')
            report.write(f'TEXT HERE ABOUT FREQUENCY OF MESSAGES/USERS DISTRIBUTION\n\n')
            report.write(f'![{ch} Messages per users distribution]({ch}_dispersion_graph.jpg)\n\n\n')

            # Adding chat sentiments to report
            report.write(f'### 3.2. Chat\'s Sentiments Analysis\n\n\n') 
            report.write(f'TEXT HERE ABOUT USERS\'S SENTIMENT\n\n')
            report.write(f'![{ch} Messages per users distribution]({ch}_sentiments_bar.jpg)\n\n\n')
            report.write(f'TEXT HERE ABOUT USERS\'S SENTIMENT\n\n')
            report.write(f'![{ch} Messages per users distribution]({ch}_sentiments_piechart.jpg)\n\n\n')

            # Adding metadata analisys to report
            report.write(f'### 3.3. Shared files\' metadata\n\n\n')
            report.write(f'TEXT HERE\n')
            
            # Adding keywords analisys to report
            report.write(f'### 3.4. Keywords Mentions\n\n\n')
            report.write(f'TEXT HERE\n')
            
            report.close()
        except Exception as e:
            print(f"[-] An error occurred: {Fore.RED}{e}{Style.RESET_ALL}")
            return []
