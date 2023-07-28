import ConexaoPostgreMPL
import ConexaoCSW
import pandas as pd


def TransformarPlanoTipoNota(plano):
    conn = ConexaoPostgreMPL.conexao()
    tiponota = pd.read_sql('SELECT "tipo nota" from pcp."tipoNotaporPlano" where plano = %s', conn,params=(plano,))
    tiponota = ', '.join(tiponota['tipo nota'])
    conn.close()
    return tiponota

def VendasporSku(plano , aprovado= True):
    tiponota = TransformarPlanoTipoNota(plano)
    conn1 = ConexaoPostgreMPL.conexao()
    vendas = pd.read_sql('SELECT * from pcp."Plano" where codigo = %s ',conn1,params=(plano,))
    conn1.close()

    iniVenda = vendas['inicioVenda'][0]
    iniVenda = iniVenda[6:] + "-" + iniVenda[3:5] + "-" + iniVenda[:2]

    finalVenda = vendas['FimVenda'][0]
    finalVenda = finalVenda[6:] + "-" + finalVenda[3:5] + "-" + finalVenda[:2]

    print(iniVenda)
    conn = ConexaoCSW.Conexao()
    # 1- Consulta de Pedidos
    Pedido = pd.read_sql(
        "SELECT codPedido, codTipoNota, dataPrevFat, codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo,qtdPecasFaturadas "
        " FROM Ped.Pedido "
        " where codEmpresa = 1 and  dataEmissao >= '"+iniVenda +"' and dataEmissao <= '"+finalVenda+"' and codTipoNota in ("+tiponota+")"
        " order by codPedido desc ",conn)

    Pedido.fillna('-', inplace=True)

    Pedido = PedidosBloqueado(Pedido)

    return Pedido


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