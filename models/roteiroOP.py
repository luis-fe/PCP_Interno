import ConexaoCSW
import pandas as pd



def Roteiro(like, empresa):
    like = "'"+like+"%'"
    conn = ConexaoCSW.Conexao()
    query = pd.read_sql('select top 2000 op.codLote, op.numeroOP, op.situacao, op.codFaseAtual, op.codSeqRoteiroAtual '
                        ' FROM tco.OrdemProd op '
                        ' WHERE op.codEmpresa = '+empresa+" and op.situacao > 0 and op.codLote like "+ like, conn )


    query2 = pd.read_sql('SELECT top 10000  r.numeroOP , r.codSeqRoteiro , r.codFase  from tco.RoteiroOP r '
                         ' WHERE r.codEmpresa = '+empresa+"  and r.codLote like "+ like, conn )


    conn.close()
    query.fillna('-', inplace=True)
    query2['codFase'] = query2['codFase'].astype(str)

    query = pd.merge(query, query2, on='numeroOP')


    query["situacaoMovOP"] = query.apply(lambda row: 'em processo' if row['codFaseAtual'] == row['codFase'] else '-', axis=1)


    return query


