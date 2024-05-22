from flask import Flask, render_template, jsonify , request, send_from_directory
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np    
from matplotlib.patches import Rectangle

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
    response = requests.get(f'https://economia.awesomeapi.com.br/xml/daily/{moeda}/{quantd_dias}')
    root = ET.fromstring(response.content)
    
    # Listas para armazenar os dados
    list_high = []
    list_low = []
    varBids = []
    bids = []
    timestamps = []

    # Iterar sobre cada item e extrair os dados especificos
    for item in root.findall('item'):

        high = float(item.find('high').text)
        low = float(item.find('low').text)
        varBid = item.find('varBid').text
        bid = item.find('bid').text
        timestamp_cod = item.find('timestamp').text 
        timestamp = datetime.utcfromtimestamp(int(timestamp_cod))

        list_high.append(high)
        list_low.append(low)
        varBids.append(varBid)
        bids.append(bid)
        timestamps.append(timestamp)

    # Criar um DataFrame 
    df = pd.DataFrame({
        'high':list_high,
        'low':list_low,
        'varBid': varBids,
        'bid': bids,
        'timestamp': timestamps
    })

    # Salvar o DataFrame em um arquivo de texto
    df.to_csv('dados.txt', sep='\t', index=False)  # sep='\t' define o separador como tabulação

    return df


def plotaSalvaGraficos(df):
    
    n = 6
    
    fig, ax = plt.subplots(figsize=(n, n))
    df['bid'] = pd.to_numeric(df['bid'])
    label_dias = np.arange(len(df['bid']))
    df['varBid'] = pd.to_numeric(df['varBid'])
    # Set the color scheme
    col_up = 'green'
    col_down = 'red'

    # GRAFICO DE VELA
    for idx, row in df.iterrows():
        if row['Close'] >= row['Open']:
            color = col_up
            lower = row['Open']
            height = row['Close'] - row['Open']
        else:
            color = col_down
            lower = row['Close']
            height = row['Open'] - row['Close']

        # Plot the candle body
        ax.add_patch(Rectangle((idx, lower), 1, height, color=color, alpha=0.7))

        # Plot the wicks
        ax.plot([idx, idx], [row['Low'], row['High']], color='black', linewidth=0.6)
        ax.plot([idx, idx], [row['Low'], lower], color=color, linewidth=0.6)
        ax.plot([idx, idx], [row['High'], lower + height], color=color, linewidth=0.6)

    # Formatting the x-axis
    ax.set_xticks(range(0, len(df.index), 5))
    #ax.set_xticklabels(df.index.strftime('%Y-%m-%d')[::5], rotation=45, ha='right')

    # Adding grid
    ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.7)

    # Adding title and labels
    ax.set_xlabel('Data', fontsize=12)
    ax.set_ylabel('Preço', fontsize=12)

    # Display the plot
    plt.tight_layout()

    # Rotating the x-axis tick labels at 30 degrees towards the right
    plt.xticks(label_dias, rotation=30, ha='right')
    # displaying candlestick chart of stock data
    # of a week

    
    # Save the figure to a BytesIO object
    path_save = os.path.join("assets", "grafico1.png")
    fig.savefig(path_save, format='png')

    #grafico de linhas ligadas
    fig = plt.figure(figsize=(10, 6.0))
    plt.plot(label_dias, df['bid'], label='MAE_H', color='darkorange')
    
    plt.xlabel('Indice')
    plt.xticks(label_dias)
    plt.ylabel('Erro(Δ)')
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
    data_inicio = datetime.strptime(data_inicio,'%Y-%m-%d').strftime('%d/%m/%Y')
    data_fim = datetime.now().strftime('%d/%m/%Y') #INPUT ESTATICO

    valor_alerta = float(request.form['valor_alerta'])

    # Realizar uma requisicao baseado em uma moeda escolhida
    requisicao = realizaReqCambio(moeda)

    # Retorna um DataFrame com o histórico que o usuario solicitou
    dadosTxCambio = retornaHistoricoMoeda(moeda, calcular_dias_periodo(data_inicio, data_fim))

    # Salva os gráficos
    plotaSalvaGraficos(dadosTxCambio)

    # Ao renderizar a pagina "resultado.html" eu passo a variavel moeda como parametro , para que eu possa realizar a rota "/get_data"
    # usando como parâmetro para requisicao essa própria variavel "moeda" , salvando esse valor enquanto navego entre as paginas
    return render_template("resultado.html" , moeda=moeda , valor_alerta = valor_alerta)

if __name__ == '__main__':
    app.run(debug=True)