# -*- coding: utf-8 -*-
"""analise_palavras_presidentes.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bAxFDOjUwyC0-UhSbiIUpdJ_8plNEJAS

# **Estudo sobre obtenção de dados do Twitter**

  Esse notebook tem por objetivo promover o estudo pratico da utilização da api do twitter para obtenção de tweets de um usuário. De modo detalhado, iniciaremos o presente notebook entendendo a forma pela qual as requisições de dados no twitter são feitas, em seguida iremos entender o formato desse dado. Após essa primeira parte, partiremos para o aprendizado de como estruturar os dados bruto em diretórios e como processar essas dados. Por fim, iremos realizar um conjunto de abordagens que visam facilitar a extração de caracteristicas dos dados.

### 1.Instalando bibliotecas 

  A linguagem a ser utilizada nesse script é o python, e o conjunto de bibliotecas necessárias para o desenvolvimento desse notebook encontram-se no arquivo requirements.txt e, para instala-los, vamos usar o instalador de pacotes do python, o pip.Para saber mais sobre o pip, ver [pip documentation](https://pip.pypa.io/en/stable/reference/pip_install/).
"""

!pip install -r requirements2.txt

"""### 2.Autenticação no twitter

  Agora que já temos todas a bibliotecas necessárias instaladas, vamos iniciar o processo de autenticação de usuário. A autenticação é necessária para que vc tenha acesso as ferramentos do twitter desenvolvidas para desenvolvedores de aplicações. Para criar uma conta developer no twitter, antes você precisa ter uma conta no [twitter](http://twitter.com.br/). Você irá encontrar informações de como ter acesso a conta developer [aqui](https://developer.twitter.com/en/apply-for-access). Depois de obtido a conta developer, suas credenciais podem ser encontradas [aqui]( https://developer.twitter.com/en/portal/dashboard).
"""

#@title Autenticando usuário 
api_key = "rRRLYoufBQukOmFeMRQyWVuG9" # API key
api_key_secret = "bPaLMINpo29tsctY4Ta7qTYBsj8iqjVnmUuijTxvAsuxK5xnZW" # API key secret
access_token = "1312228473839267841-763VxH5Op6hrbbEM321LNV0K61LnUY" # Access token
access_token_secret = "LwSyRCi195fK1JCHW5JUorK5ru4P2OMq3HileLgra1aZH" # Access token secret

import tweepy
# as variaveis api_key, api_key_secret, access_token, access_token_secret devem 
# ser inicializadas com os valores obtidos na conta developer.

# autentincando acesso na API
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)
if api.verify_credentials():
    print("Credenciais verificadas.")

"""### 3.Explorando os dados 

Antes de começar a recolher tweets dos usuários, devemos entender o formato ao qual esse dado está estruturado, então, vamos realizar a busca de um tweet especifico para isso. Vamos usar como exemplo um tweet do jogador de futebol Cristiano Ronaldo, que encontra-se no seguinte link: https://twitter.com/Cristiano/status/1311236846131658753.
"""

# recolhendo tweet por id
tweet = api.get_status(id = '1311236846131658753')
tweet

"""Como podemos ver, o status retornando é composto de um objeto identificando o tipo dos dados e seu conteúdo, em formato .json. Podemos acessar apenas o conteúdo do tweet da seguinte forma:"""

# visualizando conteúdo de um tweet
tweet._json

"""Como podemos ver, o arquivo .json é composto de <chave; valor>, valores os quais, podem conter valores 'terminais' ou outros conjuntos de <chave;valor>. É bastante importante entender o formato desse dados, pois será dele que iremos extrair informações de interesse. O acesso a informações de interesse é feito da seguinte forma:"""

print("Nome:", tweet.user.name)
print("Username do usuário:", tweet.user.screen_name)
print("Conteúdo do tweet:", tweet.text)
print("Quantidade de likes do tweet:", tweet.favorite_count)
print("Quantidade de retweets do tweet:", tweet.retweet_count)

# extraindo tweets para lista de usuários
def extract_all_tweets_for_user(api, username):

    tem_mais_tweets = True
    print(f"Recolhendo tweets para {username} ...")
    todos_tweets = []
    latest_id = None

    while tem_mais_tweets:
        tweets = api.user_timeline(screen_name = username,
                                   count = 200, 
                                   include_rts=False,
                                   max_id=latest_id,
                                   tweet_mode='extended' 
                                  )
        todos_tweets.extend(tweets)
        if not tweets:
            tem_mais_tweets = False
        else:
            latest_id = tweets[-1].id - 1

    print(f"Foram recolhidos {len(todos_tweets)} tweets.")

    return todos_tweets

# lista de usuários
usuarios = [
    'realDonaldTrump',
    'JustinTrudeau',
    'alferdez',
    'LuisLacallePou',
    'lopezobrador_',
    'jairbolsonaro',
    'sebastianpinera',
    'MartinVizcarraC',
    'MaritoAbdo',
    'Lenin',
]

# extaindo tweets par usuarios
tweet_list = []
for username in usuarios:
    user_tts = extract_all_tweets_for_user(api, username)
    tweet_list.extend(user_tts)
    
print(f"Total de tweets coletados: {len(tweet_list)}.")

# salvando os dados em disco
import os
import json
from datetime import datetime
from tqdm.notebook import tqdm 

def criando_datalake(tweet_list):
    # organizando os dados por usuário, data e hora de request
    datalake_user_path = "datalake/tweets/presidentes/{username}/dt={date}/hr={hour}"

    # escrevendo arquivos no disco
    for tweet in tqdm(tweet_list):
        now = datetime.now()
        data = now.strftime("%Y-%m-%d")
        hora = now.strftime("%H")
        username = tweet.user.screen_name

        # nome do arquivo id.json
        tweet_id = tweet.id
        
        # definindo path
        path = datalake_user_path.format(
            username = username,
            date = data,
            hour = hora
        )
        
        # criando diretório 
        os.makedirs(path, exist_ok = True)

        # definindo nome do arquivo
        fname = f"{tweet_id}.json"
        # definindo diretório que o arquivo será salvo
        fpath = os.path.join(path, fname)

        # selecionando o tweet
        dados = json.dumps(tweet._json) 

        # salvando no respectivo diretorio
        with open(fpath, 'w') as fp:
            fp.write(dados)

criando_datalake(tweet_list)

import glob
import json
import unidecode
from collections import Counter

# lendo os dados salvos em disco
files = glob.glob('datalake/tweets/presidentes/*/*/*/*')
print(f"Quantidade de tweets: {len(files)}")
files[0:10]

# explorando nossos dados
amostra = files[0]
with open(amostra, 'r') as f:
    dados = f.read()

print(f"Tipo: {type(dados)}")
print(f"Conteúdo:\n{dados[:100]}...")

# transformando dados json > dict
data = json.loads(dados)
print(f"Tipo: {type(data)}")

# iterando sobre todos campos do dicionário
for key, value in data.items():
    print("key:", key)
    print("\tvalue:", value)
    print()

# listando todos campos disponíveis
for key in data.keys():
    print(key)

print(data)

# mapeando os campos de interesse
def extract_columns(tweet):
    return {
     "id": tweet['id'],
     "created_at": tweet['created_at'],
     "username":tweet['user']['screen_name'],
     "favorite_count": tweet['favorite_count'],
     "retweet_count": tweet['retweet_count'],
     "text": tweet['full_text']
    }

# extraindo dos tweets apenas os campos de interesse
tabela_interesse = []
for fname in tqdm(files):
    with open(fname, 'r') as fp:
        tweet_json = fp.read()
    
    tweet = json.loads(tweet_json)
    linha = extract_columns(tweet)
    tabela_interesse.append(linha)

tabela_interesse[0]

"""# **4.Análisando os dados**

  Para concluir nosso estudo, vamos análisar as palavras mais utilizadas pelos presidentes dos seguintes páises: USA, Brasil, México, Argentina, Uruguai, Peru, Equador, Chile, Canada e Paraguai. O presente estudo não tem por objetivo inferir informações a respeito das análises, o principal objetivo é apenas transitar pelas metodologias e aprender as técnicas para análise de dados extraídos do twitter.
"""

import pandas as pd
import numpy as np

colunas = ['created_at', 'id', 'username', 'text', 'retweet_count', 'favorite_count']

df = pd.DataFrame(tabela_interesse, columns = colunas)

# definindo texto em inglês como string vazia (será preenchido adiante)
df['text_en'] = '' 
df.head()

# visualizando tipos dos dados
df.info()

# transformando os dados do tipo data
df['created_at']

from datetime import datetime

# aplicando trasnformção de dados (isso estrutura melhor nossos dados, facilita o processamento)
df['created_at'].apply(lambda dt: datetime.strptime(dt, '%a %b %d %H:%M:%S %z %Y'))

# transformando dados
df['created_at'] = df['created_at'].apply(lambda dt: datetime.strptime(dt, '%a %b %d %H:%M:%S %z %Y'))

df.head()

# visualizando dimensão dos dados
df.shape

# quantificando quantidade de tweets por usuario
df.groupby("username").id.count()

# quantificando a quantidade de tweets únicos por usuários
df.groupby("username").id.nunique()

# verificando presença de tweets duplicados
df.groupby("username").id.count() != df.groupby("username").id.nunique()

# criando ambiente multicore
import ray 
import psutil

num_cpus = psutil.cpu_count(logical=False)
print("Number of CPUs", num_cpus)
ray.init(num_cpus = 6) # Number of workers

# traduzindo tweets para o ingles
@ray.remote
def translate_text(text):
    translator = Translator()
    translation = translator.translate(text)
    return translation.text

from googletrans import Translator

# implementando tradução paralela
texts_pt = df['text']

batch = []
texts_en = []
batch_size = 50

for text in tqdm(texts_pt):
    batch.append(text)

    if len(batch) < batch_size:
        continue
    futures = [translate_text.remote(text) for text in batch]
    translated_texts = ray.get(futures)

    for translated in translated_texts:
        texts_en.append(translated)
    batch = []

futures = [translate_text.remote(text) for text in batch]
translated_texts = ray.get(futures)

for translated in translated_texts:
    texts_en.append(translated)

ray.shutdown()

len(texts_en) == len(texts_pt)

df['text_en'] = texts_en

df.tail()

# salvando dados processados
os.makedirs('database/trusted/presidentes/', exist_ok = True)
df.to_csv('database/trusted/presidentes/tweets.csv', index = False)

# lendo os dados
df = pd.read_csv('database/trusted/presidentes/tweets.csv')

df.head()

# quantificando quantidade de tweets por usuario
quantidade_por_usuario = df.groupby('username').id.agg('count').sort_values(ascending = False)
quantidade_por_usuario

# plotando 
quantidade_por_usuario.plot(kind = 'bar', figsize=(14,10))

# quantificando tweets com mais retweets
df.sort_values('retweet_count', ascending = False).head()

# quantificando tweets com mais likes
df.sort_values('favorite_count', ascending = False).head()

# Agrupando textos por usuário
text_por_usario = df.groupby('username').text_en.agg(list)
text_por_usuario

# fazendo download de stopwords em ingles
import nltk
nltk.download('stopwords')

from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import matplotlib.pyplot as plt
 
for i in range(len(usuarios)):
  # recolhendo o texto por usuario
  texts = text_por_usuario[usuarios[i]]
  
  # setando stopwords para o idioma ingles
  stop_words = set(stopwords.words('english')) #['https',  'co'] # O que muda ?
  stop_words.add('https')
  stop_words.add('co')
  stop_words.add('http')
  
  # criando objeto nuvem de palavras
  wordcloud = WordCloud(stopwords = stop_words,
                        background_color = "white",
                        width = 2000, height = 1200).generate(" ".join(texts))

  # criando objeto grafico
  fig, ax = plt.subplots(figsize = (15,10))
  ax.imshow(wordcloud, interpolation = 'bilinear')
  ax.set_axis_off()

  plt.savefig(f'presidente_{usuarios[i]}.png')
  plt.imshow(wordcloud);

"""**Autor:** Felipe Marcelo P. Dos Santos"""