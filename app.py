import numpy as np
from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)


# Função que realiza uma requisição de API baseado na escolha de uma moeda:
def calcular_dias_periodo(data_inicio, data_fim):
  # Converter as strings de data no formato dd/mm/yyyy para objetos datetime
  inicio = datetime.strptime(data_inicio, '%d/%m/%Y')
  fim = datetime.strptime(data_fim, '%d/%m/%Y')

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

  # Iterar sobre cada item e extrair os dados específicos
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


def plotaSalvaGraficos(df, cambio):
  # Converter colunas relevantes para numérico
  df['open'] = pd.to_numeric(df['open'])
  df['close'] = pd.to_numeric(df['close'])
  df['high'] = pd.to_numeric(df['high'])
  df['low'] = pd.to_numeric(df['low'])
  df['varBid'] = pd.to_numeric(df['varBid'])

  # Determinar os dias em que o preço da ação subiu ou desceu
  up = df[df['close'] >= df['open']]
  down = df[df['close'] < df['open']]

  # Cores para dias de alta e baixa
  col1 = 'green'
  col2 = 'red'

  # Definindo a largura dos elementos do candlestick
  width = 0.3
  width2 = 0.02

  fig, ax = plt.subplots(figsize=(10, 6))

  # Plotando preços de alta da ação
  ax.bar(up.index, up['close'] - up['open'], width, bottom=up['open'], color=col1, edgecolor='black')

  # Plotando preços de baixa da ação
  ax.bar(down.index, down['open'] - down['close'], width, bottom=down['close'], color=col2, edgecolor='black')

  # Plotando os pavios de alta-baixa
  '''for idx in df.index:
      ax.plot([idx, idx], [df.loc[idx, 'low'], df.loc[idx, 'high']], color='black')'''

  # Definindo títulos e rótulos
  ax.set_title(f"Gráfico de Vela ({cambio})")
  ax.set_xlabel('Data')
  ax.set_ylabel('Preço')

  # Formatando o eixo x para mostrar datas corretamente
  ax.set_xticklabels(df['timestamp'].dt.strftime('%Y-%m-%d'), ha='right')

  plt.tight_layout()

  path_save = os.path.join("assets", "grafico1.png")
  # fim grafico 1

  fig.savefig(path_save, format='png')

  fig, aux = plt.subplots(figsize=(10, 6))
  plt.plot(df['timestamp'], df['close'], color='darkorange')
  ax.set_xlabel('Data')
  ax.set_ylabel('Preço')
  base_font_size = 10

  if len(df['timestamp']) >= 30:
    base_font_size = base_font_size / (len(df['timestamp']) // 2)
    # Definindo o tamanho da fonte para os rótulos do eixo x
    plt.setp(ax.get_xticklabels(), fontsize=base_font_size)

  path_save = os.path.join("assets", "grafico2.png")
  fig.savefig(path_save, format='png')

  return 1


@app.route('/')
def index():
  return render_template('home.html')


@app.route('/get_data')
def get_data():
  # Pedir para o usuário passar um parâmetro na requisição "?moeda=MOEDA" para que eu possa requisitar na API
  moeda = request.args.get('moeda')

  # Faz uma requisição para a API
  response = requests.get(f'https://economia.awesomeapi.com.br/last/{moeda}')
  if response.status_code == 200:
    dados = response.json()
    moeda_formatada = moeda.replace("-", "")
    return dados[moeda_formatada]
  else:
    print("Erro ao fazer a requisição:", response.status_code)


# Rota que recupera arquivos da pasta "assets"
@app.route('/assets/<path:path>')
def send_assets(path):
  return send_from_directory('assets', path)


# ROTA PRINCIPAL que mostra a página "resultado.html"
@app.route('/enviar', methods=['POST'])
def enviar():
  # Pegar valor enviados no formulário
  moeda = request.form['moeda']
  data_inicio = request.form['data_inicio']
  data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').strftime('%d/%m/%Y')
  data_fim = datetime.now().strftime('%d/%m/%Y')  # INPUT ESTÁTICO

  valor_alerta = float(request.form['valor_alerta'])

  # Realizar uma requisição baseado em uma moeda escolhida
  requisicao = realizaReqCambio(moeda)

  # Retorna um DataFrame com o histórico que o usuário solicitou
  dadosTxCambio = retornaHistoricoMoeda(moeda, calcular_dias_periodo(data_inicio, data_fim))

  # Salva os gráficos
  plotaSalvaGraficos(dadosTxCambio, moeda)

  # Ao renderizar a página "resultado.html" eu passo a variável moeda como parâmetro, para que eu possa realizar a rota "/get_data"
  # usando como parâmetro para requisição essa própria variável "moeda", salvando esse valor enquanto navego entre as páginas
  return render_template("resultado.html", moeda=moeda, valor_alerta=valor_alerta)



if __name__ == '__main__':
    app.run(debug=True)