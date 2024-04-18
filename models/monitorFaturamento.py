import pandas as pd
import BuscasAvancadas
import ConexaoCSW
import ConexaoPostgreMPL
import datetime
import numpy
import locale
from models import controle
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

    consultar = consultar.loc[:, ['codPedido', 'codProduto', 'qtdePedida', 'qtdeFaturada', 'qtdeCancelada','qtdeSugerida','StatusSugestao','PrecoLiquido']]
    consultar = consultar.rename(columns={'StatusSugestao': 'Sugestao(Pedido)'})

    consultar['qtdeSugerida'] = consultar['qtdeSugerida'].astype(int)


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

def MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota,rotina, ip, datainicio):
    #Convertendo tipo de nota em string "1,2, 3, .."

    #tiponota2 = ""
    #for i in tiponota:
        #tiponota2 = tiponota2 + "," + i

    #tiponota2 = tiponota2[1:]

    # 1 - Carregar Os pedidos (etapa 1)
    pedidos = Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota)


    # 2 - Filtrar Apenas Pedidos Não Bloqueados
    pedidosBloqueados = Monitor_PedidosBloqueados()
    pedidos = pd.merge(pedidos,pedidosBloqueados,on='codPedido',how='left')
    pedidos['situacaobloq'].fillna('Liberado',inplace=True)
    pedidos = pedidos[pedidos['situacaobloq'] == 'Liberado']
    etapa1 = controle.salvarStatus_Etapa1(rotina, ip, datainicio, 'carregar capa dos pedidos do csw +FiltroPedidos N/Bloqueados') #Registrar etapa no controlador


    # 3- Consulta de Embarques Enviados do pedido , utilizando a consulta de notas fiscais do ERP
    entregasFaturadas = ObtendoEntregas_Enviados()
    pedidos = pd.merge(pedidos,entregasFaturadas,on='codPedido',how='left')

    # 4- Consulta de Embarques Solicitado pelo Cliente , informacao extraida do ERP
    entregasSolicitadas = ObtendoEntregasSolicitadas()
    pedidos = pd.merge(pedidos,entregasSolicitadas,on='codPedido',how='left')

    etapa2 = controle.salvarStatus_Etapa2(rotina, ip, etapa1, 'encontrar N Entregas') #Registrar etapa no controlador

    # 5 - Explodir os pedidos no nivel sku
    sku = Monitor_nivelSku(iniVenda)
    estruturasku = EstruturaSku()
        # 5.1 - Considerando somente a qtdePedida maior que 0
    pedidos = pd.merge(pedidos,sku,on='codPedido',how='left')
    pedidos = pd.merge(pedidos,estruturasku,on='codProduto',how='left')
    etapa3 = controle.salvarStatus_Etapa3(rotina, ip, etapa2, 'Explodir os pedidos no nivel sku') #Registrar etapa no controlador


    # 6 Consultando n banco de dados do ERP o saldo de estoque
    estoque = EstoqueSKU()
    pedidos = pd.merge(pedidos,estoque,on='codProduto',how='left')



    # 8 -     # Clasificando o Dataframe para analise
    pedidos = pedidos.sort_values(by='vlrSaldo', ascending=False)  # escolher como deseja classificar
    pedidos = pedidos[pedidos['vlrSaldo'] >0]


    # 9 - Obtendo o saldo sku por sku e filtrando os pedidos que ficaram com saldo  zerado
    pedidos['QtdSaldo'] = pedidos['qtdePedida']- pedidos['qtdeFaturada']-pedidos['qtdeSugerida']
    etapa4 = controle.salvarStatus_Etapa4(rotina, ip, etapa3, 'Obtendo o saldo sku por sku') #Registrar etapa no controlador


    #10 Contando o numero de ocorrencias acumulado do sku no DataFrame
    pedidos['Sku_acumula'] = pedidos.groupby('codProduto').cumcount() + 1


    #11 Trantando os valores vazios na qtdeSugerida
    #pedidos['qtdeSugerida'] = pedidos['qtdeSugerida'].replace('', numpy.nan).fillna('0')

    #12 Calculando a nova data de Previsao do pedido
    pedidos['dias_a_adicionar'] = pd.to_timedelta(pedidos['entregas_enviadas']*15, unit='d') # Converte a coluna de inteiros para timedelta
    pedidos['dataPrevAtualizada']= pd.to_datetime(pedidos['dataPrevFat'],errors='coerce', infer_datetime_format=True)
    pedidos['dataPrevAtualizada'] =  pedidos['dataPrevAtualizada'] + pedidos['dias_a_adicionar']


    #13.1 Obtendo o Estoque Liquido para o calculo da necessidade
    pedidos['EstoqueLivre'] = pedidos['estoqueAtual']-pedidos['estReservPedido']
    #13.2 Obtendo a necessidade de estoque
    pedidos['Necessidade'] = pedidos.groupby('codProduto')['QtdSaldo'].cumsum()
    #13.3 0 Obtendo a Qtd que antende para o pedido baseado no estoque
    pedidos["Qtd Atende"] = pedidos.apply(lambda row: row['QtdSaldo']  if row['Necessidade'] <= row['EstoqueLivre'] else 0, axis=1)
    pedidos["Qtd Atende"] = pedidos.apply(lambda row: row['qtdeSugerida'] if row['qtdeSugerida']>0 else row['Qtd Atende'], axis=1)
    etapa5 = controle.salvarStatus_Etapa5(rotina, ip, etapa4, 'Obtendo o Estoque Liquido para o calculo da necessidade')#Registrar etapa no controlador


    #14 Separando os pedidos a nivel pedido||engenharia||cor
    pedidos["Pedido||Prod.||Cor"] = pedidos['codPedido'].str.cat([pedidos['codItemPai'], pedidos['codCor']],
                                                                       sep='||')


    #15  Calculando a necessidade a nivel de grade Pedido||Prod.||Cor
    pedidos['Saldo +Sugerido'] = pedidos['QtdSaldo']+pedidos['qtdeSugerida']
    pedidos['Saldo Grade'] = pedidos.groupby('Pedido||Prod.||Cor')['Saldo +Sugerido'].transform('sum')

    #16 otendo a Qtd que antende para o pedido baseado no estoque e na grade
    pedidos['X QTDE ATENDE'] = pedidos.groupby('Pedido||Prod.||Cor')['Qtd Atende'].transform('sum')
    pedidos['Qtd Atende por Cor'] = pedidos.apply(lambda row: row['Saldo +Sugerido'] if row['Saldo Grade'] == row['X QTDE ATENDE'] else 0, axis=1)
    etapa6 = controle.salvarStatus_Etapa6(rotina, ip, etapa5, 'otendo a Qtd que antende para o pedido baseado no estoque e na grade')#Registrar etapa no controlador


    pedidos = pedidos.sort_values(by=['dataPrevAtualizada', 'Pedido||Prod.||Cor'],
                                        ascending=[True, True])  # escolher como deseja classificar


    #17- Indicador de % que fecha no pedido a nivel de grade Pedido||Prod.||Cor'
    pedidos['% Fecha'] = (pedidos.groupby('Pedido||Prod.||Cor')['Qtd Atende por Cor'].transform('sum')) / (
        pedidos.groupby('codPedido')['QtdSaldo'].transform('sum'))

    pedidos['% Fecha'] = pedidos['% Fecha'].round(2)

    pedidos['% Fecha Acumulado'] = (pedidos.groupby('codPedido')['Qtd Atende por Cor'].cumsum()) / (
        pedidos.groupby('codPedido')['QtdSaldo'].transform('sum'))
    pedidos['% Fecha Acumulado'] = pedidos['% Fecha Acumulado'].round(2)
    pedidos['% Fecha Acumulado'] = pedidos['% Fecha Acumulado'] * 100


    # 18 - Encontrando a Marca desejada
    pedidos['codItemPai'] = pedidos['codItemPai'].astype(str)
    pedidos['MARCA'] = pedidos['codItemPai'].apply(lambda x: x[:3])
    pedidos['MARCA'] = numpy.where(
        (pedidos['codItemPai'].str[:3] == '102') | (pedidos['codItemPai'].str[:3] == '202'), 'M.POLLO', 'PACO')


    pedidos['QtdSaldo'].fillna(0,inplace=True)
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
    try:
        pedidos['CATEGORIA'] = pedidos['nomeSKU'].apply(categorizar_produto)
    except:
        pedidos['CATEGORIA'] = '-'

    dadosConfPer = ConfiguracaoPercEntregas()
    dadosCategoria = ConfiguracaoCategoria()

    dadosCategoria = dadosCategoria.rename(columns={'Opção': 'CATEGORIA'})
    pedidos = pd.merge(pedidos,dadosCategoria,on='CATEGORIA',how='left')
    pedidos['Qtd Atende por Cor'] = pedidos.apply(lambda row: row['Qtd Atende por Cor'] if row['Status'] == '1' else 0,axis=1)
    pedidos['Qtd Atende'] = pedidos.apply(lambda row: row['Qtd Atende'] if row['Status'] == '1' else 0,axis=1)

    etapa7 = controle.salvarStatus_Etapa7(rotina, ip, etapa6, 'etapa 7')#Registrar etapa no controlador


    # Encontrando o numero restante de entregas
    pedidos['Entregas Restantes'] = pedidos['entregas_Solicitadas'] - pedidos['entregas_enviadas']
    pedidos['Entregas Restantes'] = pedidos.apply(
        lambda row: 1 if row['entregas_Solicitadas'] <= row['entregas_enviadas'] else row['Entregas Restantes'], axis=1)



    pedidos['% Fecha pedido'] = (pedidos.groupby('codPedido')['Qtd Atende por Cor'].transform('sum')) / (
        pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum'))
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido']*100
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido'].astype(float).round(2)
    pedidos['Entregas Restantes'] = pedidos.apply(
        lambda row: 1 if row['entregas_Solicitadas'] <= row['entregas_enviadas'] else row['Entregas Restantes'], axis=1)

    pedidos['Entregas Restantes'] = pedidos['Entregas Restantes'].astype(str)

    pedidos = pd.merge(pedidos, dadosConfPer, on='Entregas Restantes', how='left')

    pedidos['% Fecha pedido'] = (pedidos.groupby('codPedido')['Qtd Atende por Cor'].transform('sum')) / (pedidos.groupby('codPedido')['Saldo +Sugerido'].transform('sum'))
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido']*100
    pedidos['% Fecha pedido'] = pedidos['% Fecha pedido'].astype(float).round(2)

    # definir as condições
    condicoes = [(pedidos['% Fecha pedido'] >= pedidos['ValorMin']) &
                (pedidos['% Fecha pedido'] <= pedidos['ValorMax']),
                (pedidos['% Fecha pedido'] > pedidos['ValorMax']) &
                (pedidos['% Fecha pedido'] <= pedidos['ValorMax']),
                (pedidos['% Fecha pedido'] > pedidos['ValorMax']) &
                (pedidos['% Fecha pedido'] > pedidos['ValorMax']),
                (pedidos['% Fecha pedido'] < pedidos['ValorMin'])
                ]#

    # definir os valores correspondentes
    valores = ['SIM', 'SIM','SIM(Redistribuir)','NAO']

    # função para avaliar cada grupo
    def avaliar_grupo(df_grupo):
        if (df_grupo['Distribuicao'] == 'SIM(Redistribuir)').all():
            return 'True'
        if (df_grupo['Distribuicao'] == 'SIM').all():
            return 'True'
        else:
            return 'False'



    # atribuir os valores com base nas condições
    pedidos['Distribuicao'] = numpy.select(condicoes, valores, default=True)
    # aplicando a função para cada grupo
    df_resultado = pedidos.groupby('Pedido||Prod.||Cor').apply(avaliar_grupo).reset_index(name='Resultado')
    print(df_resultado)

    pedidos = pd.merge(pedidos, df_resultado, on='Pedido||Prod.||Cor', how='left')
    pedidos['Distribuicao2'] = pedidos.apply(lambda row: 'SIM(Redistribuir)' if row['Resultado'] == 'False'
                                                                                     and (row['Distribuicao'] == 'SIM' and row['Qtd Atende por Cor']>0 ) else row['Distribuicao'], axis=1 )


    pedidos['Valor Atende por Cor'] = pedidos['Qtd Atende por Cor'] * pedidos['PrecoLiquido']
    etapa8 = controle.salvarStatus_Etapa8(rotina, ip, etapa7, 'Obtendo valor atente por cor ')#Registrar etapa no controlador



    # Identificando a Quantidade Distribuida
    pedidos['Qnt. Cor(Distrib.)'] = pedidos.apply(
        lambda row: row['Qtd Atende por Cor'] if row['Distribuicao2'] == 'SIM' else 0, axis=1)
    pedidos['Qnt. Cor(Distrib.)'] = pedidos['Qnt. Cor(Distrib.)'].astype(int)

    pedidos['Valor Atende por Cor'] =pedidos['Valor Atende por Cor'].astype(float).round(2)
    pedidos['Valor Atende por Cor(Distrib.)'] = pedidos.apply(lambda row: row['Valor Atende por Cor'] if row['Distribuicao2'] == 'SIM' else 0, axis=1)
    pedidos['Valor Atende'] = pedidos['Qtd Atende'] * pedidos['PrecoLiquido']
    pedidos['Valor Atende'] =pedidos['Valor Atende'].astype(float).round(2)

    pedidos.to_csv('meutesteMonitor.csv')


def API(empresa, iniVenda, finalVenda, tiponota):
    pedidos = pd.read_csv('meutesteMonitor.csv')
    pedidos['codPedido'] = pedidos['codPedido'].astype(str)
    pedidos['codCliente'] = pedidos['codCliente'].astype(str)



    pedidos = pedidos.groupby('codPedido').agg({
    "MARCA": 'first',
    "codTipoNota": 'first',
    "dataPrevFat": 'first',
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
    'QtdSaldo': 'sum',
    'Qtd Atende por Cor': 'sum',
    'Valor Atende por Cor': 'sum',
    #'Valor Atende': 'sum',
    'Sugestao(Pedido)': 'first',
    'Valor Atende por Cor(Distrib.)': 'sum',
    'Qnt. Cor(Distrib.)': 'sum'
    #'observacao': 'first'
    }).reset_index()

    pedidos['%'] = pedidos['Qnt. Cor(Distrib.)']/(pedidos['Saldo +Sugerido'])
    pedidos['%'] = pedidos['%']*100
    pedidos['%'] = pedidos['%'].round(0)
    pedidos.rename(columns={'MARCA': '01-MARCA',"codPedido":"02-Pedido",
                            "codTipoNota":"03-tipoNota","dataPrevFat":"04-Prev.Original","dataPrevAtualizada":"05-Prev.Atualiz","codCliente":"06-codCliente",
                            "vlrSaldo":"08-vlrSaldo","entregas_Solicitadas":"09-Entregas Solic","entregas_enviadas":"10-Entregas Fat",
                            "ultimo_fat":"11-ultimo fat","qtdPecasFaturadas":"12-qtdPecas Fat","Qtd Atende":"13-Qtd Atende","QtdSaldo":"14- Qtd Saldo",
                            "Qnt. Cor(Distrib.)":"21-Qnt Cor(Distrib.)","%":"23-% qtd cor",
                            "Sugestao(Pedido)":"18-Sugestao(Pedido)","Qtd Atende por Cor":"15-Qtd Atende p/Cor","Valor Atende por Cor":"16-Valor Atende por Cor",
                            "Valor Atende por Cor(Distrib.)":"22-Valor Atende por Cor(Distrib.)"}, inplace=True)

    pedidos = pedidos.sort_values(by='08-vlrSaldo', ascending=False)  # escolher como deseja classificar
    pedidos["10-Entregas Fat"].fillna(0,inplace=True)
    pedidos["09-Entregas Solic"].fillna(0, inplace=True)
    pedidos["11-ultimo fat"].fillna('-', inplace=True)
    pedidos["05-Prev.Atualiz"].fillna('-', inplace=True)
    return pedidos




def ConfiguracaoPercEntregas():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql(
            """Select * from pcp.monitor_fat_dados """, conn)

    conn.close()

    return consultar


def ConfiguracaoCategoria():
    conn = ConexaoPostgreMPL.conexao()

    consultar = pd.read_sql(
            """Select * from pcp.monitor_check_status """, conn)

    conn.close()

    return consultar
