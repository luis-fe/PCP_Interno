#### Arquivo .py criado para o processo de reserva do PRE FATURAMENTO
import requests
import pandas as pd

#http://192.168.0.183:8000/pcp/api/AtualizarAutomacao


def APIAtualizaPreFaturamento():
    url = "https://192.168.0.25/api/customci/v10/atualizarSugestaoFaturamento"
    # Token de autenticação
    token = "eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJsdWlzLmZlcm5hbmRvIiwiY3N3VG9rZW4iOiJsU3NVYXNCTyIsImRiTmFtZVNwYWNlIjoiY29uc2lzdGVtIiwiaXNzIjoiYXBpIiwiYXVkIjoiYXBpIiwiZXhwIjoxODQ3ODg3Nzg3fQ.xRw6vP87ROIFCs5d - 6" \
            "T5T6LNpUf - bNsX1U2hogrsf2sbLKYKEqPTIVyPgu1YBrhEemgOhSxgEGvfFpIthDb7"
    print(token)
    headers = {'Authorization': f'{token}'}
    response = requests.get(url, headers=headers)


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

