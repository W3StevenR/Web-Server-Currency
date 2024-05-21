from flask import Flask, render_template, jsonify , request, send_from_directory
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt
import pandas as pd

app = Flask(__name__)

# Durante a execução do código , eu terei que atualizar no HTML 3 vezes (3 formas diferentes o card principal)
# 1) Quando eu clica em "Enviar Solicitação" eu deve fazer uma requisição
# 2) A cada 60s eu deve fazer outra requisição
# 3) Quando o usuário apertar o botão "atualizar" deve fazer outra requisição

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

# todo:
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

    # Exibir o DataFrame
    print(df)
    # Salvar o DataFrame em um arquivo de texto
    df.to_csv('dados.txt', sep='\t', index=False)  # sep='\t' define o separador como tabulação

    return df


def plotaSalvaGraficos(df, data_ini, data_fim):
    # dataframe de exemplo
    n = 8
    # tamanho da figura em polegadas
    fig = plt.figure(figsize=(n, n))

    # "up" dataframe will store the stock_prices
    # when the closing stock price is greater
    # than or equal to the opening stock prices
    df['bid'] = pd.to_numeric(df['bid'])
    df['varBid'] = pd.to_numeric(df['varBid'])
    up = df[df.high >= df.bid]

    # "down" dataframe will store the df
    # when the closing stock price is
    # lesser than the opening stock prices
    down = df[df.high < df.bid]

    # When the stock prices have decreased, then it
    # will be represented by blue color candlestick
    col1 = 'red'

    # When the stock prices have increased, then it
    # will be represented by green color candlestick
    col2 = 'green'

    # Setting width of candlestick elements
    width = .3
    width2 = .03

    # Plotting up prices of the stock
    plt.bar(up.index, up.high - up.bid, width, bottom=up.bid, color=col1)
    plt.bar(up.index, up.high - up.high, width2, bottom=up.high, color=col1)
    plt.bar(up.index, up.low - up.bid, width2, bottom=up.bid, color=col1)

    # Plotting down prices of the stock
    plt.bar(down.index, down.high - down.bid, width, bottom=down.bid, color=col2)
    plt.bar(down.index, down.high - down.bid, width2, bottom=down.bid, color=col2)
    plt.bar(down.index, down.low - down.high, width2, bottom=down.high, color=col2)

    # rotating the x-axis tick labels at 30degree
    # towards right
    plt.xticks(rotation=30, ha='right')

    # displaying candlestick chart of stock data
    # of a week

    plt.plot(df)
    # Save the figure to a BytesIO object
    path_save = os.path.join("assets", "grafico1.png")

    fig.savefig(path_save, format='png')

    return 1

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/get_data')
def get_data():
    # Pedir para o usuario passar um parametro na requisicao "?moeda=MOEDA" para que eu possa requisitar na API
    moeda = request.args.get('moeda')
    print(moeda)

    # Faz uma requisição para a API
    response = requests.get(f'https://economia.awesomeapi.com.br/last/{moeda}')
    if response.status_code == 200:
        dados = response.json()
        moeda_formatada = moeda.replace("-", "")
        print(dados[moeda_formatada])
        return dados[moeda_formatada]
    else:
        print("Erro ao fazer a requisição:", response.status_code)
#ROTA À ASSETS recupera arquivos

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

    # TODO:
    # Realiza Validação de daTa:
    ## Codigo aqui

    # Realizar uma requisicao baseado em uma moeda escolhida
    requisicao = realizaReqCambio(moeda)

    print(moeda , data_inicio , data_fim , valor_alerta)
    print(requisicao)

    # Retorna um DataFrame com o histórico que o usuario solicitou
    dadosTxCambio = retornaHistoricoMoeda(moeda, calcular_dias_periodo(data_inicio, data_fim))

    # Salva os gráficos
    plotaSalvaGraficos(dadosTxCambio, data_inicio, data_fim)

    # Ao renderizar a pagina "resultado.html" eu passo a variavel moeda como parametro , para que eu possa realizar a rota "/get_data"
    # usando como parâmetro para requisicao essa própria variavel "moeda" , salvando esse valor enquanto navego entre as paginas
    return render_template("resultado.html" , moeda=moeda)

if __name__ == '__main__':
    app.run(debug=True)