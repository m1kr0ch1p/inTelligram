#!/usr/bin/python

#from exiftool import ExifToolHelper
from tika import parser
from termcolor import colored

def exifExtract(imagem):
    # Parse o arquivo
    parsed = parser.from_file(imagem)

    # Obtenha os metadados
    metadata = parsed["metadata"]

    # Imprima os metadados
    for key, value in metadata.items():
        print(f"{key}: {value}")


# Menu
imagem = 'baixe_aqui_sua_apostila_caligrafia_nota_10_atualizadapdf.pdf'
#imagem = input('Informe o diretório e nome do arquivo (Ex.: /home/user/Desktop/imagem.jpg)\n')
exifExtract(imagem)

