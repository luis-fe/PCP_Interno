import ConexaoCSW
import pandas as pd



def Roteiro(like, empresa):
    like = "'"+like+"%'"
    conn = ConexaoCSW.Conexao()
    query = pd.read_sql('select top 200 op.codLote, op.numeroOP, op.situacao, op.codFaseAtual, op.codSeqRoteiroAtual '
                        ' FROM tco.OrdemProd op '
                        ' WHERE op.codEmpresa = '+empresa+" and op.situacao > 0 and op.codLote like "+ like, conn )
    conn.close()
    return query


