import pandas as pd
import requests
import ConexaoCSW
import json


def ObtendoPedidos():
    condicaoV = '1, 8, 96, 218, 220, 224, 225, 226, 227, 228, 229'
    # Dividindo a string em uma lista de valores
    condicaoV = condicaoV.split(', ')
    # Criando o DataFrame
    condicaoV = pd.DataFrame({'codCondVenda': condicaoV})

    conn = ConexaoCSW.Conexao()

    condicaotgET = CondicaoPag()

    dataFrame = pd.read_sql('SELECT s.codPedido, p.codCondVenda  from ped.SugestaoPed s '
                            'join ped.Pedido  p on  p.codEmpresa = s.codEmpresa and p.codPedido = s.codPedido  '
                            'where p.codEmpresa = 1 and s.situacaoSugestao = 0',conn)

    EmbarqueUninco = ObtendoEmbarqueUnico()
    EmbarqueUninco = pd.merge(dataFrame,EmbarqueUninco,on='codPedido')

    dataFrame = pd.merge(dataFrame, condicaotgET, on='codCondVenda')

    dataFrame = pd.merge(dataFrame, condicaoV, on='codCondVenda')

    df_union = pd.concat([dataFrame, EmbarqueUninco], ignore_index=True)
    df_union.fillna('-', inplace=True)

    return df_union
def CondicaoPag():
    conn = ConexaoCSW.Conexao()
    condicao = pd.read_sql('SELECT C.codigo as codCondVenda , C.descricao  FROM CAD.CondicaoDeVenda C WHERE C.codEmpresa = 1', conn)
    condicao['codCondVenda'] = condicao['codCondVenda'].astype(str)

    return condicao




# TIPO DE NOTA 24

def ObtendoEmbarqueUnico():

    conn = ConexaoCSW.Conexao()
    df_Entregas_Solicitadas= pd.read_sql("select top 100000 "
                                         "CAST(codPedido as varchar) as codPedido, "
                                         "numeroEntrega as entregas_Solicitadas from asgo_ped.Entregas where "
                                         "codEmpresa = 1 and numeroEntrega = 1 order by codPedido desc",conn)
    return df_Entregas_Solicitadas


def AplicandoAtualizacao():
    url = "https://192.168.0.25/api/customci/v10/atualizarSugestaoFaturamento"
    token = "eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJsdWlzLmZlcm5hbmRvIiwiY3N3VG9rZW4iOiJsU3NVYXNCTyIsImRiTmFtZVNwYWNlIjoiY29uc2lzdGVtIiwiaXNzIjoiYXBpIiwiYXVkIjoi" \
            "YXBpIiwiZXhwIjoxODQ3ODg3Nzg3fQ.xRw6vP87ROIFCs5d-6T5T6LNpUf-bNsX1U2hogrsf2sbLKYKEqPTIVyPgu1YBrhEemgOhSxgEGvfFpIthDb7AQ"


    # Defina os parâmetros em um dicionário
    params = {
        'pedido': '228268,304684'
    }

    # Defina os headers
    headers = {
        'accept': 'application/json',
        'empresa': '1',
        'Authorization': f'{token}'
    }

    # Faça a requisição POST com parâmetros e headers usando o método requests.post()
    response = requests.post(url, params=params, headers=headers,  verify=False)

    # Verifique o resultado da requisição
    if response.status_code == 200:  # Ou qualquer outro código de sucesso que a API retorne
        # Converter JSON para um dicionário Python
        dados_dict = response.json()

        # Criar o DataFrame
        df = pd.json_normalize(dados_dict)
        return df
    else:
        return pd.DataFrame({'Erro na Requisicao':False})


AplicandoAtualizacao()