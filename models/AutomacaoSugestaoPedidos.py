import pandas as pd
import requests
import ConexaoCSW
import time



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

    Marca =  pd.read_sql("SELECT t.codPedido as codPedido, case when substring(i.codItemPai,1,3) = '102' then 'M.POLLO'  "
                         " WHEN substring(i.codItemPai,1,3) = '104' then 'PACO'"
                         " WHEN substring(i.codItemPai,1,3) = '204' then 'PACO'"
                         " when substring(i.codItemPai,1,3) = '202' then 'M.POLLO' "
                         " ELSE '-' END Marca from ("
                         " select codPedido , max(produto) as produto from ped.SugestaoPedItem p"
                         " WHERE p.codEmpresa = 1 group by codPedido )t join cgi.Item2  i on i.codItem  = t.produto where i.Empresa = 1",conn)

    dataFrame = pd.merge(dataFrame, Marca, on='codPedido')
    EmbarqueUninco = ObtendoEmbarqueUnico()
    EmbarqueUninco = pd.merge(dataFrame,EmbarqueUninco,on='codPedido')

    dataFrame = pd.merge(dataFrame, condicaotgET, on='codCondVenda')

    dataFrame = pd.merge(dataFrame, condicaoV, on='codCondVenda')

    df_union = pd.concat([dataFrame, EmbarqueUninco], ignore_index=True)
    df_union.fillna('-', inplace=True)
    df_union.rename(
        columns={'codPedido': 'pedido'},
        inplace=True)

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
                                         "codEmpresa = 1  order by codPedido desc",conn)
    return df_Entregas_Solicitadas


def AplicandoAtualizacao(client_ip):
    dataframe = ObtendoPedidos()
    start_time = time.time()

    url = "https://192.168.0.25/api/customci/v10/atualizarSugestaoFaturamento"
    token = "eyJhbGciOiJFUzI1NiJ9.eyJzdWIiOiJsdWlzLmZlcm5hbmRvIiwiY3N3VG9rZW4iOiJsU3NVYXNCTyIsImRiTmFtZVNwYWNlIjoiY29uc2lzdGVtIiwiaXNzIjoiYXBpIiwiYXVkIjoi" \
            "YXBpIiwiZXhwIjoxODQ3ODg3Nzg3fQ.xRw6vP87ROIFCs5d-6T5T6LNpUf-bNsX1U2hogrsf2sbLKYKEqPTIVyPgu1YBrhEemgOhSxgEGvfFpIthDb7AQ"


    # Defina os parâmetros em um dicionário

    pedido = ','.join(dataframe['pedido'].astype(str))

    params = {
        'pedido': f'{pedido}'
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

        end_time = time.time()
        execution_time = end_time - start_time
        execution_time = round(execution_time, 2)
        execution_time = str(execution_time)

        ConexaoCSW.ControleRequisicao('Automacao Api da Sugestao Automatica Csw', execution_time, client_ip)
        # Explodir os valores das listas em colunas separadas
        df_exploded = pd.DataFrame({
            'pedidoCompleto': df['pedidoCompleto'].explode().reset_index(drop=True),
            'pedidoIncompleto': df['pedidoIncompleto'].explode().reset_index(drop=True)
        })

        # Preencher células vazias com '-' (ou outro valor desejado)
        df_exploded = df_exploded.fillna('-')
        # Derreter o DataFrame para criar a coluna "pedido" e "situacao"
        df_melted = pd.melt(df_exploded, value_vars=['pedidoCompleto', 'pedidoIncompleto'], var_name='situacao',
                            value_name='pedido')

        # Mapear os valores de "situacao" para "completo" e "incompleto"
        df_melted['situacao'] = df_melted['situacao'].map(
            {'pedidoCompleto': 'completo', 'pedidoIncompleto': 'incompleto'})

        # Remover linhas com valor "-"
        df_melted = df_melted[df_melted['pedido'] != '-']

        df_melted = pd.merge(df_melted,dataframe,on='pedido')



        return df_melted
    else:
        return pd.DataFrame({'Erro na Requisicao':False})
