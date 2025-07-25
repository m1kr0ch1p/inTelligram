import os
import sys
sys.path.append('engines/')
from PyPDF2 import PdfReader
import exifread
from docx import Document
from colorama import Fore, Style

# Loading list of channels
def load_channel_list(file_path='engines/channels.txt'):
    with open(file_path, "r") as file:
        return [line.strip() for line in file]

# Extract PDF metadata
def pdf_extract(path):
    try:
        reader = PdfReader(path)
        info = reader.metadata
        #print(f'{info}\n')
        print(f'    - Author: {info.author}')
        print(f'    - Creator: {info.creator}')
        print(f'    - Creation date: {info.creation_date}')
        print(f'    - Modification date: {info.modification_date}')
        print(f'    - Producer: {info.producer}')
    except Exception as e:
        print(f'Error - {e}')

# image extensions
def image_extract(path):
    try:
        with open(path, 'rb') as f:
            tags = exifread.process_file(f)
            for tag in tags.keys():
                if tag == "JPEGThumbnail":
                    pass
                else:
                    print(f'    - {tag}: {tags[tag]}')

    except Exception as e:
        print(f'Error - {e}')

# .zip and .rar files
def doc_extract(path):
    try:
        doc = Document(path)
        core_properties = doc.core_properties
        print(f'    - Author: {core_properties.author}')
        print(f'    - Creation date: {core_properties.created}')
        print(f'    - Language: {core_properties.language}')
        print(f'    - Last modified by: {core_properties.last_modified_by}')
        print(f'    - Last modified date: {core_properties.modified}')
    except Exception as e:
        print(f'Error - {e}')

# compacted files
def comp_extract(file):
    print(f'{file} is a compacted format file.')

# Extracts metadata from downloaded files
def file_treatment():
    # Setting local variables
    import platform
    channel_list = load_channel_list()
    list_dir = os.listdir
    operating_system = platform.system()

    # Stderr to null
    if operating_system == 'Linux':
        sys.stderr = open('/dev/null', 'w')
    elif operating_system == 'Windows':
        sys.stderr = open('NUL','w')

    # Extracting metadata from files directory
    for channel_name in channel_list:
        ch = channel_name.rsplit("/",1)[-1]
        down_dr = f'CaseFiles/{ch}/downloaded_files'
        files = list_dir(down_dr)
        try:
            print(f"[+] Extracting Metadata from downloaded files from {Fore.LIGHTYELLOW_EX}{ch}{Style.RESET_ALL}...")
            sys.stdout = open(f'{down_dr}/{ch}_downloadedExif.md', 'w')
            print(f'## Extracting Metadata in {ch}\n\n')
            for file in files:
                try:
                    path = f'{down_dr}/{file}'

                    if file.lower().endswith(('.jpg', '.png')):
                        print(f'[+] {file} is an image file.')
                        image_extract(path)
                    elif file.lower().endswith('.pdf'):
                        print(f'[+] {file} is a PDF file.')
                        pdf_extract(path)
                    elif file.lower().endswith(('.doc', '.docx')):
                        print(f'[+] {file} is a DOC file.')
                        doc_extract(path)
                    elif file.lower().endswith(('.zip', '.rar')):
                        print(f'[+] {file} is a compressed file.')
                        comp_extract(path)
                    else:
                        print(f'[-] Another format to {file}')
                except Exception as e:
                    print(f'Error - {e}')
        except:
            print(f"{Fore.YELLOW}[-] Maybe there is no file shared by chat's members... :( {Style.RESET_ALL}")
        sys.stdout.close()  # Fecha o arquivo
        sys.stdout = sys.__stdout__  # Restaura o stdout original
