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
        "SELECT top 100 codPedido, codTipoNota, dataPrevFat, codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo,qtdPecasFaturadas "
        " FROM Ped.Pedido "
        " where codEmpresa = 1 and  dataEmissao >= '"+iniVenda +"'"
        " order by codPedido desc ",conn)


    return Pedido

#--and codTipoNota in ( %s ) and  dataEmissao >= %s and dataEmissao <= %s, params=(iniVenda,finalVenda,)