#### Arquivo .py criado para o processo de reserva do PRE FATURAMENTO
import requests
import pandas as pd

import BuscasAvancadas
import ConexaoCSW


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
        coluna1 = pd.DataFrame(df_exploded['pedidoCompleto'])
        coluna1['situacao Pedido'] = 'completo'
        coluna1.rename(columns={'pedidoCompleto': 'codPedido'}, inplace=True)
        coluna2 = pd.DataFrame(df_exploded['pedidoIncompleto'])
        coluna2['situacao Pedido'] = 'Incompleto'
        coluna2.rename(columns={'pedidoIncompleto': 'codPedido'}, inplace=True)

        concatenar = pd.concat([coluna1, coluna2])

        return concatenar


    else:
        print('Falha ao obter os dados da API')



def StatusSugestaoPedidos():
    #pedidos = APIAtualizaPreFaturamento()
    conn = ConexaoCSW.Conexao()

    entrega = pd.read_sql(BuscasAvancadas.ObtendoEmbarqueUnico(),conn)
    pedidos= pd.read_sql(BuscasAvancadas.CapaSugestoes(),conn)
    condicoespgto =pd.read_sql(BuscasAvancadas.CondicoesDePGTO(),conn) #codCondVenda
    condicoespgto['codCondVenda'] = condicoespgto['codCondVenda'].astype(str)
    pedidos['codCondVenda'] = pedidos['codCondVenda'].astype(str)

    conn.close()

    pedidos = pd.merge(pedidos,entrega,on='codPedido',how='left')
    pedidos = pd.merge(pedidos,condicoespgto,on='codCondVenda',how='left')
    pedidos.fillna('',inplace=True)
    pedidos['descricao'] = pedidos['codCondVenda'] +'-'+pedidos['descricao']
    #pedidos = pd.merge(pedidos,capaSugestao,on='codPedido',how='left')
    pedidos['prioridadeReserva'] = '-'
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['descricao'],row['prioridadeReserva']),axis=1)


    return pedidos


def VerificaACondicao(descricaoPagto, retorno):

    if retorno == '-' and '177' in descricaoPagto:
        return '1- A VISTA Antecipado'
    else:
        return retorno



