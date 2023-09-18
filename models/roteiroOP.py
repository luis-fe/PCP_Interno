import ConexaoCSW
import pandas as pd
import numpy



def Roteiro(like, empresa):
    like = "'"+like+"%'"
    conn = ConexaoCSW.Conexao()
    query = pd.read_sql('select  op.codLote, op.numeroOP, op.situacao, op.codFaseAtual, op.codSeqRoteiroAtual '
                        ' FROM tco.OrdemProd op '
                        ' WHERE op.codEmpresa = '+empresa+" and op.situacao > 1 and op.codLote like "+ like, conn )


    query2 = pd.read_sql('SELECT  r.numeroOP , r.codSeqRoteiro , r.codFase  from tco.RoteiroOP r '
                         ' WHERE r.codEmpresa = '+empresa+"  and r.codLote like "+ like, conn )

    query3 = pd.read_sql('select ot.numeroOP , ot.codItem, ot.codSortimento, ot.qtdePecas1Qualidade '
                         'FROM tco.OrdemProdTamanhos ot '
                         ' WHERE ot.codEmpresa = ' + empresa + "  and ot.codLote like " + like, conn)


    conn.close()
    query['codSeqRoteiroAtual']  = query['codSeqRoteiroAtual'] .replace('', numpy.nan).fillna('0')
    query.fillna('-', inplace=True)
    query2['codFase'] = query2['codFase'].astype(str)
    query['codSeqRoteiroAtual'] = query['codSeqRoteiroAtual'].astype(int)



    query = pd.merge(query, query2, on='numeroOP')


    query["situacaoMovOP"] = query.apply(lambda row: 'em processo' if row['codFaseAtual'] == row['codFase']
        else '-', axis=1)

    query["situacaoMovOP"] = query.apply(lambda row: 'em fila'
    if row['situacaoMovOP'] != 'em processo' and row['codSeqRoteiro'] > row['codSeqRoteiroAtual']
        else row['situacaoMovOP'], axis=1)

    query["situacaoMovOP"] = query.apply(lambda row: 'movimentado'
    if row['situacaoMovOP'] == '-' or row['situacao']== '2'
        else row['situacaoMovOP'], axis=1)

    query = pd.merge(query, query3, on='numeroOP')

    query.to_csv('roteiro_op.csv')




    return pd.DataFrame({'Mensagem': 'sucesso'})


