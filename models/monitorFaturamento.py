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


    pedidos.to_csv('meutesteMonitor.csv')



    return pedidos





