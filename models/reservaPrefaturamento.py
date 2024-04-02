#### Arquivo .py criado para o processo de reserva do PRE FATURAMENTO
import requests
import pandas as pd

#http://192.168.0.183:8000/pcp/api/AtualizarAutomacao


def APIAtualizaPreFaturamento():
    url = "http://192.168.0.183:8000/pcp/api/AtualizarAutomacao"
    response = requests.get(url)
    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Converter os dados JSON em um dicionário
        data = response.json()

        # Criar um DataFrame a partir do dicionário
        df = pd.DataFrame(data)

        # Exibir o DataFrame
        print(df)
    else:
        print('Falha ao obter os dados da API')

