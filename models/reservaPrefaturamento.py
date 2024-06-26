#### Arquivo .py criado para o processo de reserva do PRE FATURAMENTO
import requests
import pandas as pd

import BuscasAvancadas
import ConexaoCSW
import ConexaoPostgreMPL
import datetime
import pytz
def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.datetime.now(fuso_horario)
    agora = agora.strftime('%d/%m/%Y %H:%M:%S')
    return agora

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

    # Defina os parâmetros em um dicionário
    dataframe = StatusSugestaoPedidos()
    pedido = ','.join(dataframe['codPedido'].astype(str))

    params = {
        'pedido': f'{pedido}'
    }

    # Faça a requisição POST com parâmetros e headers usando o método requests.post()
    response = requests.post(url,  headers=headers,params=params,  verify=False)


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

        concatenar = pd.merge(dataframe, concatenar, on='codPedido',how='left')

        Atualizado = obterHoraAtual()

        concatenar['Atualizado'] = Atualizado

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


    #Buscando os faturamentos das sugestoes

    faturamentos = pd.read_sql(BuscasAvancadas.BuscarFaturamentoSugestoes(),conn)
    faturamentos['entregas_realiadas'] = 1
    faturamentos = faturamentos.groupby(['codPedido']).agg({
        'dataFaturamento': 'max',
        'entregas_realiadas': 'count'
    }).reset_index()
    pedidos = pd.merge(pedidos,faturamentos,on='codPedido',how='left')
    pedidos['entregas_realiadas'].fillna(0,inplace=True)

    sugestaoItem = pd.read_sql(BuscasAvancadas.SugestaoItemAberto(),conn)
    sugestaoItem = sugestaoItem.groupby(['codPedido']).agg({
        'qtdeSugerida': 'sum'
    }).reset_index()

    pedidos = pd.merge(pedidos,sugestaoItem,on=['codPedido'],how='left')

    conn.close()

    pedidos = pd.merge(pedidos,entrega,on='codPedido',how='left')
    pedidos = pd.merge(pedidos,condicoespgto,on='codCondVenda',how='left')
    pedidos.fillna('',inplace=True)
    pedidos['descricao'] = pedidos['codCondVenda'] +'-'+pedidos['descricao']
    #pedidos = pd.merge(pedidos,capaSugestao,on='codPedido',how='left')
    pedidos['prioridadeReserva'] = '-'
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['descricao'],row['prioridadeReserva'],'1 -A VISTA ANTECIPADO','Antecipado'),axis=1)
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['descricao'],row['prioridadeReserva'],'2 - CARTAO','CART'),axis=1)
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['entregas_Solicitadas'],row['prioridadeReserva'],'3 - EMBARQUE UNICO',1.0),axis=1)
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['entregas_Solicitadas'],row['prioridadeReserva'],'3 - EMBARQUE UNICO','-'),axis=1)
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['entregas_Solicitadas'],row['prioridadeReserva'],'3 - EMBARQUE UNICO','-'),axis=1)
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['codTipoNota'],row['prioridadeReserva'],'4 - MPLUS','39-'),axis=1)
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['descricao'],row['prioridadeReserva'],'5 - OUTROS','None-'),axis=1)
    pedidos['prioridadeReserva'] = pedidos.apply(lambda row: VerificaACondicao(row['descricao'],row['prioridadeReserva'],'5 - OUTROS',' DD'),axis=1)


    pedidos = pedidos.sort_values(by=['prioridadeReserva'],
                                          ascending=True)  # escolher como deseja classificar


    PedidosItemGradeSugestao_ = PedidosItemGradeSugestao()
    pedidos = pd.merge(pedidos,PedidosItemGradeSugestao_,on='codPedido',how='left')

    pedidos.fillna('-',inplace=True)

    return pedidos


def VerificaACondicao(descricaoPagto, prioridade, retorno, refe):

    refe = str(refe)
    descricaoPagto = str(descricaoPagto)
    if prioridade == '-' and refe in descricaoPagto:
        return retorno
    else:
        retorno = prioridade
        return retorno


def PedidosItemGradeSugestao():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql('select * from "PCP".pcp."pedidosItemgrade" ig ',conn) #codPedido, codProduto, qtdePedida, qtdeFaturada, qtdeCancelada
    consultar['qtdeSugerida'].fillna(0,inplace=True)
    conn.close()

    consultar["Pçaberto"] = consultar['qtdePedida'] -consultar['qtdeCancelada'] -consultar['qtdeFaturada']
    consultar["QtdePedida"] = consultar['qtdePedida']-consultar['qtdeCancelada']
    consultar = consultar.groupby(['codPedido']).agg({
        'Pçaberto': 'sum',
        'QtdePedida':'sum'

    }).reset_index()


    return consultar
