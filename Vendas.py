import numpy

import ConexaoPostgreMPL
import ConexaoCSW
import pandas as pd

def Comparacao(a , b, c, valor):
    if valor <= a:
        return 'A'
    elif valor <= b:
        return 'B'
    else:
        return 'C'

def TransformarPlanoTipoNota(plano):
    conn = ConexaoPostgreMPL.conexao()
    tiponota = pd.read_sql('SELECT "tipo nota" from pcp."tipoNotaporPlano" where plano = %s', conn,params=(plano,))
    tiponota = ', '.join(tiponota['tipo nota'])
    conn.close()
    return tiponota

def VendasporSku(plano , aprovado= True, excel = False):
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


        if excel == False:

            conn = ConexaoCSW.Conexao()
            # 1- Consulta de Pedidos
            Pedido = pd.read_sql(
                "SELECT codPedido, codTipoNota, dataPrevFat, codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo,qtdPecasFaturadas "
                " FROM Ped.Pedido "
                " where codEmpresa = 1 and  dataEmissao >= '"+iniVenda +"' and dataEmissao <= '"+finalVenda+"' and codTipoNota in ("+tiponota+")"
                " order by codPedido desc ",conn)

            Pedido.fillna('-', inplace=True)

            if aprovado == True:
                Pedido = PedidosBloqueado(Pedido)
            else:
                Pedido = Pedido

            sku = ExplosaoPedidoSku(iniVenda,finalVenda)
            Pedido = pd.merge(Pedido,sku,on='codPedido',how='left')
            Pedido.to_csv(nomeArquivo)
            Pedido = Pedido.groupby('engenharia').agg({
                'engenharia': 'first',
            'qtdePedida': 'sum'})
            conn.close()
            Pedido['Total Produtos'] = Pedido['engenharia'].count()
            return Pedido
        else:
            Pedido = pd.read_csv(nomeArquivo)
            Pedido = Pedido.groupby('engenharia').agg({
                'engenharia': 'first',
                'qtdePedida': 'sum'})
            print('excel True')
            Pedido['engenharia'] = Pedido['engenharia'].astype(str)
            Pedido.sort_values(by='qtdePedida', inplace=True, ascending=False )
            Pedido['MARCA'] = numpy.where((Pedido['engenharia'].str[:3] == '102') | (Pedido['engenharia'].str[:3] == '202'),
                                            'M.POLLO', 'PACO')
            Pedido['Total Produtos'] = Pedido.groupby('MARCA')['engenharia'].transform('count')
            Pedido['ABC%'] = Pedido.groupby('MARCA')['engenharia'].cumcount() + 1
            Pedido['ABC%'] = (100 *(Pedido['ABC%']/Pedido['Total Produtos'])).round(2)

            a, b, c = ABC_Plano(plano)

            Pedido['classABC'] = Pedido.apply(lambda row: Comparacao(a, b, c,row['ABC%']), axis=1)


            return Pedido

def ABC_Plano(plano):
    conn = ConexaoPostgreMPL.conexao()
    query = pd.read_sql('Select  a, b, c from pcp."ABC_Plano" WHERE plano = %s ',conn,params=(plano,))

    return query['a'][0],query['b'][0],query['c'][0]










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
    df_ItensPedidos = pd.read_sql(
        "select top 350000 item.codPedido, item.CodItem as seqCodItem, item.codProduto, item.precoUnitario, item.tipoDesconto, item.descontoItem, case when tipoDesconto = 1 then ( (item.qtdePedida * item.precoUnitario) - item.descontoItem)/item.qtdePedida when item.tipoDesconto = 0 then (item.precoUnitario * (1-(item.descontoItem/100))) else item.precoUnitario end  PrecoLiquido from ped.PedidoItem as item WHERE item.codEmpresa = 1 order by item.codPedido desc",
        conn)
    df_SkuPedidos = pd.read_sql(
        "select  now() as atualizacao, codPedido, codItem as seqCodItem, codProduto as reduzido, "
        " (select i.coditempai as engenharia from cgi.item2 i where p.codProduto = i.coditem and i.empresa = 1) as engenharia , "
        " (select i.nome from cgi.item i where p.codProduto = i.codigo) as nome_red, "
        "qtdeCancelada, qtdeFaturada, qtdePedida  from ped.PedidoItemGrade  p where codEmpresa = 1  "
        "and codPedido in ("
        " select codPedido from Ped.Pedido where codEmpresa = 1 and  dataEmissao >= '"+datainicio +"' and dataEmissao <= '"+datafinal+"' "
        ")",conn)
    conn.close()
    return df_SkuPedidos
