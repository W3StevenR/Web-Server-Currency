function fetchData() {
            // Faz uma requisição AJAX para a rota '/get_data' do Flask
            fetch('/get_data')
                .then(response => response.json())
                .then(data => {
                    // Atualiza os dados na página
                    document.getElementById('data').innerHTML = `
                        <p>Alta: ${data.high}</p>
                        <p>Baixa: ${data.low}</p>
                        <p>Variação: ${data.varBid}</p>
                        <p>Porcentagem de Mudança: ${data.pctChange}</p>
                        <p>Oferta: ${data.bid}</p>
                        <p>Pergunte: ${data.ask}</p>
                        <p>Data e Hora: ${data.create_date}</p>
                    `;
                });
        }

// Chama a função fetchData a cada 60 segundos
setInterval(fetchData, 60000);

// Chama a função fetchData quando a página é carregada
fetchData();