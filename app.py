import numpy as np
from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)


# Funcao que realiza uma requisicao de API baseado na escolha de uma moeda:
def calcular_dias_periodo(data_inicio, data_fim):
  # Converter as strings de data no formato dd/mm/yyyy para objetos datetime
  inicio = datetime.strptime(data_inicio, f'%d/%m/%Y')
  fim = datetime.strptime(data_fim, f'%d/%m/%Y')

  # Calcular a diferença entre as duas datas
  diferenca = fim - inicio

  # Retornar o número de dias no período
  return diferenca.days


def realizaReqCambio(moeda):
  # Faz uma requisição para a API
  response = requests.get(f'https://economia.awesomeapi.com.br/last/{moeda}')
  if response.status_code == 200:
    dados = response.json()
    moeda_formatada = moeda.replace("-", "")
    return dados[moeda_formatada]
  else:
    print("Erro ao fazer a requisição:", response.status_code)


def retornaHistoricoMoeda(moeda, quantd_dias):
  response = requests.get(f'https://economia.awesomeapi.com.br/xml/daily/{moeda}/{quantd_dias + 1}')
  root = ET.fromstring(response.content)

  # Listas para armazenar os dados
  list_high = []
  list_low = []
  varBids = []
  bids = []
  timestamps = []

  # Iterar sobre cada item e extrair os dados especificos
  prev_close = None
  opens = list()
  for item in root.findall('item'):

    high = float(item.find('high').text)
    low = float(item.find('low').text)
    varBid = item.find('varBid').text
    bid = item.find('bid').text
    timestamp_cod = item.find('timestamp').text
    timestamp = datetime.utcfromtimestamp(int(timestamp_cod))

    if prev_close is None:
      opens.append(bid)  # Use bid for the first open
    else:
      opens.append(prev_close)

    list_high.append(high)
    list_low.append(low)
    varBids.append(varBid)
    bids.append(bid)
    timestamps.append(timestamp)
    prev_close = bid

  # Criar um DataFrame
  df = pd.DataFrame({
    'high': list_high,
    'low': list_low,
    'varBid': varBids,
    'open': opens,
    'close': bids,
    'timestamp': timestamps
  })

  # Salvar o DataFrame em um arquivo de texto
  df.to_csv('dados.txt', sep='\t', index=False)  # sep='\t' define o separador como tabulação

  return df


def plotaSalvaGraficos(df):
  # Convert relevant columns to numeric
  df['open'] = pd.to_numeric(df['open'])
  df['close'] = pd.to_numeric(df['close'])
  df['high'] = pd.to_numeric(df['high'])
  df['low'] = pd.to_numeric(df['low'])
  df['varBid'] = pd.to_numeric(df['varBid'])

  # Determine the days when stock price went up or down
  up = df[df['close'] >= df['open']]
  down = df[df['close'] < df['open']]

  # Colors for up and down days
  col1 = 'green'
  col2 = 'red'

  # Setting width of candlestick elements
  width = 0.3
  width2 = 0.02

  fig, ax = plt.subplots(figsize=(10, 6))

  # Plotting up prices of the stock
  ax.bar(up.index, up['close'] - up['open'], width, bottom=up['open'], color=col1, edgecolor='black')

  # Plotting down prices of the stock
  ax.bar(down.index, down['open'] - down['close'], width, bottom=down['close'], color=col2, edgecolor='black')

  # Plotting the high-low wicks
  '''for idx in df.index:
        ax.plot([idx, idx], [df.loc[idx, 'low'], df.loc[idx, 'high']], color='black')'''

  # Setting titles and labels
  ax.set_title('Candlestick Chart')
  ax.set_xlabel('Date')
  ax.set_ylabel('Price')

  # Formatting the x-axis to show dates properly
  ax.set_xticks(df.index)
  ax.set_xticklabels(df['timestamp'].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')

  # Setting titles and labels
  ax.set_title('Candlestick Chart')
  ax.set_xlabel('Date')
  ax.set_ylabel('Price')

  # Formatting the x-axis to show dates properly
  ax.set_xticks(df.index)
  ax.set_xticklabels(df['timestamp'].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')
  plt.tight_layout()

  path_save = os.path.join("assets", "grafico1.png")

  fig.savefig(path_save, format='png')

  fig, aux = plt.subplots(figsize=(10, 6))
  plt.plot(df['timestamp'], df['close'], color='darkorange')
  plt.xlabel('Indice')
  plt.xticks(df['timestamp'])
  path_save = os.path.join("assets", "grafico2.png")

  fig.savefig(path_save, format='png')

  return 1


@app.route('/')
def index():
  return render_template('home.html')


@app.route('/get_data')
def get_data():
  # Pedir para o usuario passar um parametro na requisicao "?moeda=MOEDA" para que eu possa requisitar na API
  moeda = request.args.get('moeda')

  # Faz uma requisição para a API
  response = requests.get(f'https://economia.awesomeapi.com.br/last/{moeda}')
  if response.status_code == 200:
    dados = response.json()
    moeda_formatada = moeda.replace("-", "")
    return dados[moeda_formatada]
  else:
    print("Erro ao fazer a requisição:", response.status_code)


#Rota que recupera arquivos da pasta "assets"
@app.route('/assets/<path:path>')
def send_assets(path):
  return send_from_directory('assets', path)


# ROTA PRINCIPAL que mostra a página "resulta.html"
@app.route('/enviar', methods=['POST'])
def enviar():
  # Pegar valor enviados no formulario
  moeda = request.form['moeda']
  data_inicio = request.form['data_inicio']
  data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%d/%m/%Y')
  data_fim = datetime.now().strftime('%d/%m/%Y')  #INPUT ESTATICO

  valor_alerta = float(request.form['valor_alerta'])

  # Realizar uma requisicao baseado em uma moeda escolhida
  requisicao = realizaReqCambio(moeda)

  # Retorna um DataFrame com o histórico que o usuario solicitou
  dadosTxCambio = retornaHistoricoMoeda(moeda, calcular_dias_periodo(data_inicio, data_fim))

  # Salva os gráficos
  plotaSalvaGraficos(dadosTxCambio)

  # Ao renderizar a pagina "resultado.html" eu passo a variavel moeda como parametro , para que eu possa realizar a rota "/get_data"
  # usando como parâmetro para requisicao essa própria variavel "moeda" , salvando esse valor enquanto navego entre as paginas
  return render_template("resultado.html", moeda=moeda, valor_alerta=valor_alerta)


if __name__ == '__main__':
  app.run(debug=True)
