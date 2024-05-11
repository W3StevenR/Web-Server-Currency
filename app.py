from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/get_data')
def get_data():
  # Faz uma requisição para a API
  response = requests.get('https://economia.awesomeapi.com.br/last/USD-BRL')
  data = response.json()
  return jsonify(data['USDBRL'])


if __name__ == '__main__':
  app.run(debug=True)
