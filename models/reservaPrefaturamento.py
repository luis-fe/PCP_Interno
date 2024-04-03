#### Arquivo .py criado para o processo de reserva do PRE FATURAMENTO
import requests
import pandas as pd

#http://192.168.0.183:8000/pcp/api/AtualizarAutomacao


def APIAtualizaPreFaturamento():
    url = "https://192.168.0.25/api/customci/v10/atualizarSugestaoFaturamento"
    token = "eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJsdWlzLmZlcm5hbmRvIiwiY3N3VG9rZW4iOiJsU3NVYXNCTyIsImRiTmFtZVNwYWNlIjoiY29uc2lzdGVtIiwiaXNzIjoiYXBpIiwiYXVkIjoi" \
            "YXBpIiwiZXhwIjoxODQ3ODg3Nzg3fQ.xRw6vP87ROIFCs5d-6T5T6LNpUf-bNsX1U2hogrsf2sbLKYKEqPTIVyPgu1YBrhEemgOhSxgEGvfFpIthDb7AQ"


    # Defina os parâmetros em um dicionário

    # Defina os headers
    headers = {
        'accept': 'application/json',
        'empresa': '1',
        'Authorization': f'{token}'
    }

    # Faça a requisição POST com parâmetros e headers usando o método requests.post()
    response = requests.post(url,  headers=headers,  verify=False)


    # Verificar se a requisição foi bem-sucedida
    if response.status_code == 200:
        # Converter os dados JSON em um dicionário
        dados_dict = response.json()

        # Criar o DataFrame
        df = pd.json_normalize(dados_dict)
        df_exploded = pd.DataFrame({
            'pedidoCompleto': df['pedidoCompleto'].explode().reset_index(drop=True),
            'pedidoIncompleto': df['pedidoIncompleto'].explode().reset_index(drop=True)
        })
        print(df_exploded)


        """
        # Exibir o DataFrame
        # Explodir as listas em colunas separadas
        df_exploded = df.apply(pd.Series.explode)
        coluna1 = pd.DataFrame(df_exploded['pedidoCompleto'])
        coluna1['situacao'] = 'completo'
        coluna2 = pd.DataFrame(df_exploded['pedidoIncompleto'])
        coluna2.rename(columns={'coluna2': 'pedidoCompleto'}, inplace=True)
        coluna2['situacao'] = 'incompleto'
        
        concatenar = pd.concat([coluna1, coluna2])

        """

        print(df)
    else:
        print('Falha ao obter os dados da API')

