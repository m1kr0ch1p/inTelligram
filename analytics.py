#!/usr/bin/python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import os

# cria nuvem de palavras com os textos compartilhados

def word_cloud(df,ch):
    from wordcloud import WordCloud

    texto = ''.join(map(str, df['Text']))

    wc = WordCloud(width = 800, height = 400, background_color = 'white').generate(texto)

    # Plot da nuvem de palavra
    plt.figure(figsize = (12, 6))
    plt.imshow(wc, interpolation = 'bilinear')
    plt.axis('off')
    plt.title(f'Conteudo de texto do Grupo {ch}\n')
    plt.show()

    wordcloud.to_file(f'{ch}.png')

# atribui valor aos usernames de acordo com mensagens postadas
def usernameMetric(df, ch):

    # Contando o número de mensagens por usuário
    contagem_usuarios = df.groupby('Username')['Text'].count().reset_index()
    contagem_usuarios.columns = ['Username', 'Quantidade_Mensagens']

    # Criando o gráfico de bolhas
    fig = px.scatter(contagem_usuarios, 
                     x='Username', 
                     y='Quantidade_Mensagens', 
                     size='Quantidade_Mensagens', 
                     color='Quantidade_Mensagens',
                     hover_name='Username',
                     hover_data={'Usuario_Index': False},  # Oculta o índice no hover
                     title='Quantidade de Mensagens por Usuário',
                     labels={'Quantidade_Mensagens': 'Número de Mensagens'},)
                     #size_max=60)

    # Personalizando o layout
    fig.update_layout(
        xaxis_title='Usuários',
        yaxis_title='Número de Mensagens',
        coloraxis_colorbar_title='Número de Mensagens'
    )

    # Ajustando a posição dos rótulos no eixo x
    fig.update_xaxes(tickangle=45)

    # Exibindo o gráfico
    fig.show()


# cria lista de Usernames
def usernames_list(df,ch):

    directory = f'CaseFiles/{ch}'

    unique_usernames = df['Username'].unique()
    sorted_usernames = sorted(map(str, unique_usernames))

    # salva em arquivo
    filename = f'{directory}/usernames_{ch}'
    with open(filename, 'w') as f:
        for username in sorted_usernames:
            f.write(f'{username}\n')
    print(f'Usernames from {ch} stored in {filename}.')

# chama as funcoes de analise
def analyse(csv_filename,channel_name_filtered):
    # carrega o dataframe
    ch = channel_name_filtered
    df = pd.read_csv(csv_filename)

    # shape
    df.shape

    usernames_list(df,ch)
    usernameMetric(df,ch)
    word_cloud(df,ch)

