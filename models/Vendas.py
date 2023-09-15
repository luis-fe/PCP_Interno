import numpy
import time

import pandas as pd

from models import FuncoesGlobais
import ConexaoPostgreMPL
import ConexaoCSW


def Comparacao(a , b, c, valor):
    if valor <= a:
        return 'A⭐'
    elif valor <= b:
        return 'B🥈'
    else:
        return 'C💢'

def TransformarPlanoTipoNota(plano):
    conn = ConexaoPostgreMPL.conexao()
    tiponota = pd.read_sql('SELECT "tipo nota" from pcp."tipoNotaporPlano" where plano = %s', conn,params=(plano,))
    tiponota = ', '.join(tiponota['tipo nota'])
    conn.close()
    return tiponota

def VendasporSku(client_ip,plano , aprovado= True, excel = False,pagina=0 ,itensPag=1, engenharia = '0', descricao = '0', categoria = '0', MARCA = '0' ):
    tiponota = TransformarPlanoTipoNota(plano)
    conn1 = ConexaoPostgreMPL.conexao()
    vendas = pd.read_sql('SELECT * from pcp."Plano" where codigo = %s ',conn1,params=(plano,))
    conn1.close()
    vendas.fillna('-', inplace=True)

    iniVenda = vendas['inicioVenda'][0]
    iniVenda = iniVenda[6:] + "-" + iniVenda[3:5] + "-" + iniVenda[:2]

    finalVenda = vendas['FimVenda'][0]
    finalVenda = finalVenda[6:] + "-" + finalVenda[3:5] + "-" + finalVenda[:2]
    nomeArquivo = f'Plano_{plano}_in_{iniVenda}_fim_{finalVenda}.csv'
    print(iniVenda)

    if vendas['inicioVenda'][0] == '-' or vendas['FimVenda'][0] == '-':

        return pd.DataFrame([{'Status':False, "Mensagem":f'Nao há data de inicio de vendas cadastrado no Plano {plano}'}])

    else:


        if excel == False and pagina ==0  and engenharia == '0'and descricao == '0' and categoria == '0' and MARCA == '0':

            conn = ConexaoCSW.Conexao()
            start_time = time.time()

            # 1- Consulta de Pedidos
            Pedido = pd.read_sql(
                "SELECT dataEmissao, codPedido, "
                "(select c.nome as nome_cli from fat.cliente c where c.codCliente = p.codCliente) as nome_cli, "
                " codTipoNota, dataPrevFat, codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo,qtdPecasFaturadas "
                " FROM Ped.Pedido p"
                " where codEmpresa = 1 and  dataEmissao >= '"+iniVenda +"' and dataEmissao <= '"+finalVenda+"' and codTipoNota in ("+tiponota+")"
                " order by codPedido desc ",conn)

            Pedido.fillna('-', inplace=True)

            if aprovado == True:
                Pedido = PedidosBloqueado(Pedido)
            else:
                Pedido = Pedido

            sku = ExplosaoPedidoSku(iniVenda,finalVenda)
            Pedido = pd.merge(Pedido,sku,on='codPedido',how='left')
            Pedido = Pedido.loc[(Pedido['qtdeFaturada'] == 0) & (Pedido['bloqMotEspPed'] == "0")]

            descricao = pd.read_sql("select distinct e.descricao, SUBSTRING (e.codEngenharia, 2,8) as engenharia  from tcp.engenharia e where e.codEmpresa = 1 and codEngenharia not like '6%' and codEngenharia like '%-0%' ",conn)
            Pedido['engenharia'] = Pedido['engenharia'].astype(str)

            end_time = time.time()
            execution_time = end_time - start_time
            execution_time = round(execution_time, 2)
            execution_time = str(execution_time)
            ConexaoCSW.ControleRequisicao('Consultar Venda SKU Csw', execution_time, client_ip)
            conn.close()
            Pedido = pd.merge(Pedido,descricao,on='engenharia',how='left')

            Pedido.to_csv(nomeArquivo)
            Pedido = Pedido.groupby('engenharia').agg({
                'engenharia': 'first',
                'descricao': 'first',
                'qtdePedida': 'sum',
                'qtdeFaturada': 'sum'
            })
            Pedido['engenharia'] = Pedido['engenharia'].astype(str)
            Pedido['qtdePedida'] = Pedido['qtdePedida'].astype(int)
            Pedido['Total Produtos'] = Pedido['engenharia'].count()


            Pedido.sort_values(by='qtdePedida', inplace=True, ascending=False )
            Pedido['MARCA'] = numpy.where((Pedido['engenharia'].str[:3] == '102') | (Pedido['engenharia'].str[:3] == '202'),
                                            'M.POLLO', 'PACO')
            Pedido['Total Produtos'] = Pedido.groupby('MARCA')['engenharia'].transform('count')
            Pedido['ABC%'] = Pedido.groupby('MARCA')['engenharia'].cumcount() + 1
            Pedido['ABC%'] = (100 *(Pedido['ABC%']/Pedido['Total Produtos'])).round(2)

            a, b, c = ABC_Plano(plano)
            if a == False:
                return pd.DataFrame([{'Status':False, "Mensagem":"Nao foi encontrado ABC para o Plano"}])
            else:

                Pedido['categoria'] = '-'
                Pedido['classABC'] = Pedido.apply(lambda row: Comparacao(a, b, c,row['ABC%']), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('POLO', row['descricao'],'POLO',row['categoria'] ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('TSHIRT', row['descricao'],'CAMISETA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('REGATA', row['descricao'],'CAMISETA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('BABY', row['descricao'],'CAMISETA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('SHORT', row['descricao'],'BOARDSHORT',row['categoria']  ), axis=1)

                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('CAMISA', row['descricao'],'CAMISA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('BATA', row['descricao'],'CAMISA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('MEIA', row['descricao'],'MEIA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('CUECA', row['descricao'],'CUECA',row['categoria']  ), axis=1)
                Pedido['ABC%Categ'] = Pedido.groupby(['MARCA','categoria'])['engenharia'].cumcount() + 1
                Pedido['Total ProdutosCategoria'] = Pedido.groupby(['MARCA','categoria'])['engenharia'].transform('count')
                Pedido['ABC%Categ'] = (100 *(Pedido['ABC%Categ']/Pedido['Total ProdutosCategoria'])).round(2)
                Pedido['classABC_Cat'] = Pedido.apply(lambda row: Comparacao(a, b, c,row['ABC%Categ']), axis=1)
                Pedido, totalPg = FuncoesGlobais.TemPaginamento(pagina, itensPag, Pedido, 'engenharia')
                data = {'0-numero de paginas':f'{totalPg}',
                        '1- Dados:':Pedido.to_dict(orient='records')}

                return [data], nomeArquivo

        else:
            Pedido = pd.read_csv(nomeArquivo)
            Pedido = Pedido.groupby('engenharia').agg({
                'engenharia': 'first',
                'descricao': 'first',
                'qtdePedida': 'sum',
                'qtdeFaturada':'sum'})
            print('excel True')
            Pedido['engenharia'] = Pedido['engenharia'].astype(str)
            Pedido['qtdePedida'] = Pedido['qtdePedida'].astype(int)

            Pedido.sort_values(by='qtdePedida', inplace=True, ascending=False )
            Pedido['MARCA'] = numpy.where((Pedido['engenharia'].str[:3] == '102') | (Pedido['engenharia'].str[:3] == '202'),
                                            'M.POLLO', 'PACO')
            Pedido['Total Produtos'] = Pedido.groupby('MARCA')['engenharia'].transform('count')
            Pedido['ABC%'] = Pedido.groupby('MARCA')['engenharia'].cumcount() + 1
            Pedido['ABC%'] = (100 *(Pedido['ABC%']/Pedido['Total Produtos'])).round(2)

            a, b, c = ABC_Plano(plano)
            if a == False:
                return pd.DataFrame([{'Status':False, "Mensagem":"Nao foi encontrado ABC para o Plano"}])
            else:
                Pedido['categoria'] = '-'
                Pedido['classABC'] = Pedido.apply(lambda row: Comparacao(a, b, c,row['ABC%']), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('POLO', row['descricao'],'POLO',row['categoria'] ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('TSHIRT', row['descricao'],'CAMISETA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('REGATA', row['descricao'],'CAMISETA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('BABY', row['descricao'],'CAMISETA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('SHORT', row['descricao'],'BOARDSHORT',row['categoria']  ), axis=1)

                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('CAMISA', row['descricao'],'CAMISA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('BATA', row['descricao'],'CAMISA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('MEIA', row['descricao'],'MEIA',row['categoria']  ), axis=1)
                Pedido['categoria'] = Pedido.apply(lambda row: Categoria('CUECA', row['descricao'],'CUECA',row['categoria']  ), axis=1)
                Pedido['ABC%Categ'] = Pedido.groupby(['MARCA','categoria'])['engenharia'].cumcount() + 1
                Pedido['Total ProdutosCategoria'] = Pedido.groupby(['MARCA','categoria'])['engenharia'].transform('count')
                Pedido['ABC%Categ'] = (100 *(Pedido['ABC%Categ']/Pedido['Total ProdutosCategoria'])).round(2)
                Pedido['classABC_Cat'] = Pedido.apply(lambda row: Comparacao(a, b, c,row['ABC%Categ']), axis=1)
                # Aqui Verifico se tem paginamento
                # Aqui verifico se tem filtros
                Pedido = TemFiltro(engenharia, Pedido, 'engenharia')
                Pedido = TemFiltro(descricao.upper(), Pedido, 'descricao')
                Pedido = TemFiltro(categoria.upper(), Pedido, 'categoria')
                Pedido = TemFiltro(MARCA.upper(), Pedido, 'MARCA')


                Pedido.fillna('-', inplace=True)
                Pedido, totalPg = FuncoesGlobais.TemPaginamento(pagina, itensPag, Pedido, 'engenharia')

                data = {'0-numero de paginas':f'{totalPg}',
                        '1- Dados:':Pedido.to_dict(orient='records')}

                return [data], nomeArquivo

def ABC_Plano(plano):
    conn = ConexaoPostgreMPL.conexao()
    query = pd.read_sql('Select  a, b, c from pcp."ABC_Plano" WHERE plano = %s ',conn,params=(plano,))
    if query.empty:

        return False, False, False
    else:

        return (query['a'][0] * 100),(query['b'][0]*100),(query['c'][0]*100)










def PedidosBloqueado(df_Pedidos):
    conn = ConexaoCSW.Conexao()

    # 4 - Conulta de Bloqueio Comerial do Pedidos
    df_BloqueioComercial = pd.read_sql(
        "SELECT codPedido, situacaoBloq from ped.PedidoBloqComl WHERE codEmpresa = 1 ",
        conn)
    # 4.1 Unindo o Pedido com a situação do Bloqueio Comercial, preservando a Consulta Pedidos
    df_Pedidos = pd.merge(df_Pedidos, df_BloqueioComercial, on='codPedido', how='left')
    # 4.2 - Conulta de Bloqueio Credito do Pedidos
    df_BloqueioCredito = pd.read_sql(
        "SELECT situacao, codPedido, Empresa, bloqMotEspPed FROM Cre.PedidoCreditoBloq WHERE Empresa  = 1 ",
        conn)
    # 4.2.1 Unindo o Pedido com a situação do Bloqueio Credito, preservando a Consulta Pedidos
    df_Pedidos = pd.merge(df_Pedidos, df_BloqueioCredito, on='codPedido', how='left')
    # 4.3 Filtro para puxar somente os pedidos APROVADOS
    df_Pedidos = df_Pedidos.loc[(df_Pedidos['situacao'] != "1") & (df_Pedidos['situacaoBloq'] != "1")]

    conn.close()
    return  df_Pedidos


def ExplosaoPedidoSku(datainicio, datafinal):
    conn = ConexaoCSW.Conexao()
    # 8 - Consultando o banco de dados do ERP no nivel de Pedios SKU
    #df_ItensPedidos = pd.read_sql(
     #   "select top 350000 item.codPedido, item.CodItem as seqCodItem, item.codProduto, item.precoUnitario, item.tipoDesconto, item.descontoItem, case when tipoDesconto = 1 then ( (item.qtdePedida * item.precoUnitario) - item.descontoItem)/item.qtdePedida when item.tipoDesconto = 0 then (item.precoUnitario * (1-(item.descontoItem/100))) else item.precoUnitario end  PrecoLiquido from ped.PedidoItem as item WHERE item.codEmpresa = 1 order by item.codPedido desc",
     #   conn)
    df_SkuPedidos = pd.read_sql(
        "select top 2000000 now() as atualizacao, codPedido, codItem as seqCodItem, codProduto as reduzido, "
        " (select i.coditempai as engenharia from cgi.item2 i where p.codProduto = i.coditem and i.empresa = 1) as engenharia , "
        " (select i.nome from cgi.item i where p.codProduto = i.codigo) as nome_red, "
        "qtdeCancelada, qtdeFaturada, qtdePedida  from ped.PedidoItemGrade  p where codEmpresa = 1 order by codpedido desc  ",conn)

    conn.close()
    return df_SkuPedidos

def Categoria(contem, valorReferencia, valorNovo, categoria):
    if contem in valorReferencia:
        return valorNovo
    else:
        return categoria



def TemFiltro(nomedofiltro,dataframe, coluna):
    if nomedofiltro == '0':
        estrutura = dataframe
        return estrutura
    else:
        dataframe = dataframe[dataframe[coluna].str.contains(nomedofiltro)]
        dataframe = dataframe.reset_index(drop=True)
        print(coluna)
        return dataframe

def Detalha_EngenhariaABC(engenharias, nomeArquivo):
    df = pd.read_csv(nomeArquivo)
    df = df[df['engenharia'].isin(engenharias)]
    df = df.groupby(['engenharia','codPedido']).agg({
        'engenharia': 'first',
        'codPedido': 'first',
        'dataEmissao':'first',
        'dataPrevFat':'first',
        'descricao': 'first',
        'qtdePedida': 'sum',
        'qtdeFaturada': 'sum'})
    return df


def PedidosAbertos(empresa, dataInicio, dataFim, aprovado = True):
    conn = ConexaoCSW.Conexao()
    tiponota = '1, 2, 3, 4, 5, 6, 7, 8'

    # 1- Consulta de Pedidos
    start_time = time.time() # Iniciar o relogio para registrar o tempo da query

    Pedido = pd.read_sql(
        "SELECT now() as atualizacao, dataEmissao, codPedido, "
        "(select c.nome as nome_cli from fat.cliente c where c.codCliente = p.codCliente) as nome_cli, "
        " codTipoNota, dataPrevFat, codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo, qtdPecasFaturadas "
        " FROM Ped.Pedido p"
        " where codEmpresa = "+ empresa +" and  dataEmissao >= '" + dataInicio + "' and dataEmissao <= '" + dataFim + "' and codTipoNota in (" + tiponota + ")"
        " order by codPedido desc ",conn)

    # 1.1 registrar o tempo de execucao dessa query
    end_time = time.time()
    execution_time = end_time - start_time
    execution_time = round(execution_time, 2)
    execution_time = str(execution_time)
    ConexaoCSW.ControleRequisicao('Consultar Pedido entre datas', execution_time, 'Automacao BI')

    Pedido.fillna('-', inplace=True) # aqui limpo os possiveis Null's do dataframe



    if aprovado == True:
        Pedido = PedidosBloqueado(Pedido)
    else:
        Pedido = Pedido

    # 2- Consulta de Pedidos a nivel de Sku
    start_time = time.time()# Iniciar o relogio para registrar o tempo da query
    sku = pd.read_sql(
        "select top 2000000  codPedido, codProduto as reduzido, "
        "qtdeCancelada, qtdeFaturada, qtdePedida  from ped.PedidoItemGrade  p where codEmpresa = 1 order by codpedido desc  ",conn)
    end_time = time.time()
    execution_time = end_time - start_time
    execution_time = round(execution_time, 2)
    execution_time = str(execution_time)
    ConexaoCSW.ControleRequisicao('Consultar ultimos 2 milhao pedItemGrade', execution_time, 'Automacao BI')

    Pedido = pd.merge(Pedido, sku, on='codPedido', how='left')
    Pedido = Pedido.loc[(Pedido['situacao'] != "1") & (Pedido['situacaoBloq'] != "1")]


    # 5- Consulta de Embarques Enviados do pedido , utilizando a consulta de notas fiscais do ERP
    df_Entregas_Enviados= pd.read_sql("select  top 300000 codPedido, count(codNumNota) as entregas_enviadas, "
                                      "max(dataFaturamento) as ultimo_fat from fat.NotaFiscal  where codEmpresa = 1 and codRepresentante "
                                      "not in ('200','800','300','600','700','511') and situacao = 2  group by codPedido order by codPedido desc",conn)
    #5.1 Unindo a tabela pedidos com a quantidade de embarques entregues - preservando a tabela pedidos
    Pedido = pd.merge(Pedido,df_Entregas_Enviados, on = 'codPedido', how='left')
    #5.2 Fortando a coluna Entrega Enviadas
    Pedido['entregas_enviadas'] = Pedido['entregas_enviadas'].fillna(0)
    Pedido['entregas_enviadas'] = Pedido['entregas_enviadas'].astype(int)
    # 6- Consulta de Embarques Solicitado pelo Cliente , informacao extraida do ERP
    df_Entregas_Solicitadas= pd.read_sql("select top 100000 CAST(codPedido as varchar) as codPedido,numeroEntrega as entregas_Solicitadas from asgo_ped.Entregas where codEmpresa = 1 order by codPedido desc",conn)
    # 6.1 - Unindo a tabela pedidos com a quantidade de embarques solicitados - Preservando a tabela de pedidos
    Pedido = pd.merge(Pedido,df_Entregas_Solicitadas, on = 'codPedido', how='left')
    # 6.2 Fortando a coluna Entrega Enviadas
    Pedido['entregas_Solicitadas'] = Pedido['entregas_Solicitadas'].fillna(0)
    Pedido['entregas_Solicitadas'] = Pedido['entregas_Solicitadas'].astype(int)
    Pedido['dias_a_adicionar'] = pd.to_timedelta(Pedido['entregas_enviadas']*15, unit='d') # Converte a coluna de inteiros para timedelta
    Pedido['dataPrevAtualizada'] = pd.to_datetime(Pedido['dataPrevFat'], errors='coerce',
                                                      infer_datetime_format=True)
    Pedido['dataPrevAtualizada'] = Pedido.apply(lambda row: row['dataPrevAtualizada'] + row['dias_a_adicionar'],
                                                        axis=1)
    # 8.1 Consultando n banco de dados do ERP o saldo de estoque
    df_estoque = pd.read_sql(
        "select dt.reduzido, SUM(dt.estoqueAtual) as estoqueAtual, sum(estReservPedido) as estReservPedido from  "
        "(select codItem as reduzido, estoqueAtual,estReservPedido  from est.DadosEstoque where codEmpresa = 1 and codNatureza = 5 and estoqueAtual > 0 "
        "UNION "
        "select  ot.codItem as reduzido , ot.qtdePecas1Qualidade as estoqueAtual, 0 as estReservPedido  from Tco.OrdemProd o "
        "join Tco.OrdemProdTamanhos ot on ot.codEmpresa = o.codEmpresa and ot.numeroOP = o.numeroOP "
        "WHERE o.codEmpresa = 1 and o.situacao = 3 and o.codFaseAtual = '210' and ot.qtdePecas1Qualidade is not null and codItem is not null) dt "
        "group by dt.reduzido ", conn)
    Pedido = pd.merge(Pedido, df_estoque, on='reduzido', how='left')
    # 10 - Consultando a Sugestao do Pedido a Nivel de SKU
    df_sugestao = pd.read_sql('SELECT top 1000000 codPedido , produto as reduzido, qtdePecasConf , qtdeSugerida  from ped.SugestaoPedItem WHERE codEmpresa =1 ORDER by codPedido desc',conn)

    #11- Consultando a Sugesteao de Peidos no nivel de capa e trazendo a hora da listagem
    df_sugestao_capa =pd.read_sql("SELECT codPedido, situacaoSugestao, dataHoraListagem, case when (situacaoSugestao = 2 and dataHoraListagem>0) then 'Sugerido(Em Conferencia)' WHEN situacaoSugestao = 0 then 'Sugerido(Gerado)' WHEN situacaoSugestao = 2 then 'Sugerido(A listar)' else '' end StatusSugestao from ped.SugestaoPed WHERE codEmpresa = 1 and situacaoSugestao <> 3",conn)

    conn.close() # Fechando a conexao com o banco

    # 12- Realizando o join entre Sugestao nivel sku e sugestao de capa
    df_sugestao = pd.merge(df_sugestao,df_sugestao_capa,on='codPedido')
    # 12.1 - Transferindo a Informação para o dataframe de Pedidos
    Pedido = pd.merge(Pedido,df_sugestao,on=['codPedido','reduzido'], how='left')

    Pedido['qtdeSugerida'] = Pedido['qtdeSugerida'].replace('', numpy.nan).fillna('0')
    Pedido['qtdeSugerida'] = Pedido['qtdeSugerida'].astype(int)


    Pedido['QtdSaldo'] = Pedido['qtdePedida'] - Pedido['qtdeFaturada'] - Pedido['qtdeSugerida']- Pedido['qtdeCancelada']
    Pedido['reduzido'] = Pedido['reduzido'].astype(str)
    # Clasificando o Dataframe para analise
    Pedido = Pedido.sort_values(by='dataPrevAtualizada', ascending=True)  # escolher como deseja classificar
    Pedido['EstoqueLivre'] = Pedido['estoqueAtual'] - Pedido['estReservPedido']

    # Apenas fazer a Necessidade dos pedidos "sem sugestao"

    Pedido['Necessidade'] = Pedido.groupby('reduzido')['QtdSaldo'].cumsum()
    Pedido['Saldo +Sugerido'] = Pedido['QtdSaldo'] + Pedido['qtdeSugerida']
    Pedido["Qtd Atende"] = Pedido.apply(
        lambda row: row['QtdSaldo'] if row['Necessidade'] <= row['EstoqueLivre'] else 0, axis=1)
    Pedido["Qtd Atende"] = Pedido.apply(
        lambda row: row['qtdeSugerida'] if row['qtdeSugerida'] > 0 else row['Qtd Atende'], axis=1)




    Pedido.fillna('-', inplace=True)
    Pedido = Pedido[0:400000]
    Pedido.to_csv('Pedidos_teste.csv')

    return pd.DataFrame({'status:',True})

def abrircsv(ini, fim):
    ini = int(ini)
    fim = int(fim)
    pedidos = pd.read_csv("Pedidos_teste.csv")
    pedidos.fillna('-', inplace=True)
    pedidos = pedidos[ini:fim]

    return pedidos







