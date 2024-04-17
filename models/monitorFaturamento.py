import pandas as pd
import BuscasAvancadas
import ConexaoCSW
import ConexaoPostgreMPL
import datetime
import numpy
import locale

#Carregando a Capa de pedidos do CSW : BuscasAvancadas.CapaPedido (empresa, iniVenda, finalVenda, tiponota):
def Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota):
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.CapaPedido(empresa, iniVenda, finalVenda, tiponota), conn)

    conn.close()
    return consulta


# Verfiicando se o pedido nao está bloqueado :
def Monitor_PedidosBloqueados():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.SituacaoPedidos(), conn)

    conn.close()
    return consulta


#Carregando os Pedidos a nivel Sku
def Monitor_nivelSku(datainicio):
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql("""select * from "PCP".pcp."pedidosItemgrade" ig 
where ig."dataEmissao":: date >= %s """,conn,params=(datainicio,)) #codPedido, codProduto, qtdePedida, qtdeFaturada, qtdeCancelada
    consultar['qtdeSugerida'].fillna(0,inplace=True)
    conn.close()

    consultar = consultar.loc[:, ['codPedido', 'codProduto', 'qtdePedida', 'qtdeFaturada', 'qtdeCancelada','qtdeSugerida']]

    return consultar

#EstoquePorSku
def EstoqueSKU():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.ConsultaEstoque(), conn)

    conn.close()
    return consulta

#ObtendoEntregasSolicitadas
def ObtendoEntregasSolicitadas():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.ObtendoEmbarqueUnico(), conn)

    conn.close()
    return consulta


#Entregas_Enviados
def ObtendoEntregas_Enviados():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.Entregas_Enviados(), conn)

    conn.close()
    return consulta

#Obtendo os Sku - estrutura
def EstruturaSku():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql("""Select "codSKU" as "codProduto", "codItemPai", "codCor", "nomeSKU" from pcp."SKU" """,conn)

    conn.close()

    return consultar

def MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota):
    #Convertendo tipo de nota em string "1,2, 3, .."

    tiponota2 = ""
    for i in tiponota:
        tiponota2 = tiponota2 + "," + i

    tiponota2 = tiponota2[1:]

    # 1 - Carregar Os pedidos (etapa 1)
    pedidos = Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota)

    # 2 - Filtrar Apenas Pedidos Não Bloqueados
    pedidosBloqueados = Monitor_PedidosBloqueados()
    pedidos = pd.merge(pedidos,pedidosBloqueados,on='codPedido',how='left')
    pedidos['situacaobloq'].fillna('Liberado',inplace=True)
    pedidos = pedidos[pedidos['situacaobloq'] == 'Liberado']

    # 3- Consulta de Embarques Enviados do pedido , utilizando a consulta de notas fiscais do ERP
    entregasFaturadas = ObtendoEntregas_Enviados()
    pedidos = pd.merge(pedidos,entregasFaturadas,on='codPedido',how='left')

    # 4- Consulta de Embarques Solicitado pelo Cliente , informacao extraida do ERP
    entregasSolicitadas = ObtendoEntregasSolicitadas()
    pedidos = pd.merge(pedidos,entregasSolicitadas,on='codPedido',how='left')


    # 5 - Explodir os pedidos no nivel sku
    sku = Monitor_nivelSku(iniVenda)
    estruturasku = EstruturaSku()
        # 5.1 - Considerando somente a qtdePedida maior que 0
    pedidos = pd.merge(pedidos,sku,on='codPedido',how='left')
    pedidos = pd.merge(pedidos,estruturasku,on='codProduto',how='left')

    # 6 Consultando n banco de dados do ERP o saldo de estoque
    estoque = EstoqueSKU()
    pedidos = pd.merge(pedidos,estoque,on='codProduto',how='left')



    # 8 -     # Clasificando o Dataframe para analise
    pedidos = pedidos.sort_values(by='vlrSaldo', ascending=False)  # escolher como deseja classificar
    pedidos = pedidos[pedidos['vlrSaldo'] >0]


    # 9 - Obtendo o saldo sku por sku e filtrando os pedidos que ficaram com saldo  zerado
    pedidos['QtdSaldo'] = pedidos['qtdePedida']- pedidos['qtdeFaturada']-pedidos['qtdeSugerida']
    pedidos = pedidos[pedidos['QtdSaldo']>0]


    pedidos['Sku_acumula'] = pedidos.groupby('codProduto').cumcount() + 1
    pedidos['qtdeSugerida'] = pedidos['qtdeSugerida'].replace('', numpy.nan).fillna('0')

    pedidos['dias_a_adicionar'] = pd.to_timedelta(pedidos['entregas_enviadas']*15, unit='d') # Converte a coluna de inteiros para timedelta
    pedidos['dataPrevAtualizada']= pd.to_datetime(pedidos['dataPrevFat'],errors='coerce', infer_datetime_format=True)
    pedidos['dataPrevAtualizada'] =  pedidos['dataPrevAtualizada'] + pedidos['dias_a_adicionar']

    pedidos['EstoqueLivre'] = pedidos['estoqueAtual']-pedidos['estReservPedido']
    pedidos['Necessidade'] = pedidos.groupby('codProduto')['QtdSaldo'].cumsum()
    pedidos['Saldo +Sugerido'] = pedidos['QtdSaldo']+pedidos['qtdeSugerida']
    pedidos["Qtd Atende"] = pedidos.apply(lambda row: row['QtdSaldo']  if row['Necessidade'] <= row['EstoqueLivre'] else 0, axis=1)
    pedidos["Qtd Atende"] = pedidos.apply(lambda row: row['qtdeSugerida'] if row['qtdeSugerida']>0 else row['Qtd Atende'], axis=1)

    pedidos["Pedido||Prod.||Cor"] = pedidos['codPedido'].str.cat([pedidos['codItemPai'], pedidos['codCor']],
                                                                       sep='||')
    pedidos['Saldo Grade'] = pedidos.groupby('Pedido||Prod.||Cor')['Saldo +Sugerido'].transform('sum')
    pedidos['X QTDE ATENDE'] = pedidos.groupby('Pedido||Prod.||Cor')['Qtd Atende'].transform('sum')
    pedidos['Qtd Atende por Cor'] = pedidos.apply(
        lambda row: row['Saldo +Sugerido'] if row['Saldo Grade'] == row['X QTDE ATENDE'] else 0, axis=1)

    pedidos = pedidos.sort_values(by=['dataPrevAtualizada', 'Pedido||Prod.||Cor'],
                                        ascending=[True, True])  # escolher como deseja classificar

    pedidos['% Fecha'] = (pedidos.groupby('Pedido||Prod.||Cor')['Qtd Atende por Cor'].transform('sum')) / (
        pedidos.groupby('codPedido')['QtdSaldo'].transform('sum'))
    pedidos['% Fecha'] = pedidos['% Fecha'].round(2)
    pedidos['% Fecha Acumulado'] = (pedidos.groupby('codPedido')['Qtd Atende por Cor'].cumsum()) / (
        pedidos.groupby('codPedido')['QtdSaldo'].transform('sum'))
    pedidos['% Fecha Acumulado'] = pedidos['% Fecha Acumulado'].round(2)
    pedidos['% Fecha Acumulado'] = pedidos['% Fecha Acumulado'] * 100


    pedidos['MARCA'] = pedidos['codItemPai'].apply(lambda x: x[:3])
    pedidos['MARCA'] = numpy.where(
        (pedidos['codItemPai'].str[:3] == '102') | (pedidos['codItemPai'].str[:3] == '202'), 'M.POLLO', 'PACO')

    pedidos['QtdSaldo'] = pedidos['QtdSaldo'].astype(int)
    pedidos['Qtd Atende por Cor'] = pedidos['Qtd Atende por Cor'].astype(int)
    pedidos['Qtd Atende'] = pedidos['Qtd Atende'].astype(int)
    pedidos['dataPrevAtualizada'] = pedidos['dataPrevAtualizada'].dt.strftime('%d/%m/%Y')

    # função para verificar a presença de "casa" no valor da coluna "produto"
    def categorizar_produto(produto):
        if 'JAQUETA' in produto:
            return 'AGASALHOS'
        elif 'BLUSAO' in produto:
            return 'AGASALHOS'
        elif 'TSHIRT' in produto:
            return 'CAMISETA'
        elif 'POLO' in produto:
            return 'POLO'
        elif 'SUNGA' in produto:
            return 'SUNGA'
        elif 'CUECA' in produto:
            return 'CUECA'
        elif 'CALCA/BER MOLETOM  ' in produto:
            return 'CALCA/BER MOLETOM '
        elif 'CAMISA' in produto:
            return 'CAMISA'
        elif 'SHORT' in produto:
            return 'BOARDSHORT'
        elif 'TRICOT' in produto:
            return 'TRICOT'
        elif 'BABY' in produto:
            return 'CAMISETA'
        elif 'BATA' in produto:
            return 'CAMISA'
        elif 'CALCA' in produto:
            return 'CALCA/BER MOLETOM'
        elif 'CARTEIRA' in produto:
            return 'ACESSORIOS'
        elif 'BONE' in produto:
            return 'ACESSORIOS'
        elif 'TENIS' in produto:
            return 'CALCADO'
        elif 'CHINELO' in produto:
            return 'CALCADO'
        elif 'MEIA' in produto:
            return 'ACESSORIOS'
        elif 'BLAZER' in produto:
            return 'AGASALHOS'
        elif 'CINTO' in produto:
            return 'ACESSORIOS'
        elif 'REGATA' in produto:
            return 'ACESSORIOS'
        elif 'BERMUDA' in produto:
            return 'CALCA/BER MOLETOM'
        elif 'COLETE' in produto:
            return 'AGASALHOS'
        elif 'NECESSA' in produto:
            return 'ACESSORIOS'
        elif 'CARTA' in produto:
            return 'ACESSORIOS'
        elif 'SACOL' in produto:
            return 'ACESSORIOS'
        else:
            return '-'

    #df_Pedidos['CATEGORIA'] = df_Pedidos['CATEGORIA'] .astype(str)
    try:
        pedidos['CATEGORIA'] = pedidos['nomeSKU'].apply(categorizar_produto)
    except:
        pedidos['CATEGORIA'] = '-'

    pedidos['Entrgas Restantes'] = pedidos['entregas_Solicitadas'] - pedidos['entregas_enviadas']
    pedidos['Entrgas Restantes'] = pedidos.apply(
        lambda row: 1 if row['entregas_Solicitadas'] <= row['entregas_enviadas'] else row['Entrgas Restantes'], axis=1)

    pedidos['% Fecha pedido'] = (pedidos.groupby('codPedido')['Qtd Atende por Cor'].transform('sum')) / (
        pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum'))
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido']*100
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido'].astype(float).round(2)

    pedidos.to_csv('meutesteMonitor.csv')


def API(empresa, iniVenda, finalVenda, tiponota):
    pedidos = pd.read_csv('meutesteMonitor.csv')
    pedidos = pedidos.groupby('codPedido').agg({
    "MARCA": 'first',
    "codTipoNota": 'first',
    #"dataPrevFat": 'first',
    "dataPrevAtualizada": 'first',
    "codCliente": 'first',
    #"razao": 'first',
    "vlrSaldo": 'first',
    #"descricaoCondVenda": 'first',
    "entregas_Solicitadas": 'first',
    "entregas_enviadas": 'first',
    "qtdPecasFaturadas": 'first',
    'Saldo +Sugerido':'sum',
    "ultimo_fat": "first",
    "Qtd Atende": 'sum',
    'QtdSaldo': 'sum'
    #'Qtd Atende por Cor': 'sum'
    #'Valor Atende por Cor': 'sum'
    #'Valor Atende': 'sum'
    #'Sugestao(Pedido)': 'first',
    #'Valor Atende por Cor(Distrib.)': 'sum',
    #'Qnt. Cor(Distrib.)': 'sum',
    #'observacao': 'first'
    }).reset_index()


    return pedidos





