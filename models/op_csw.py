# Importando os itens para o postgree, acionado via automacao diaria
import ConexaoCSW
import pandas as pd
import time

def ItensCSW(i, paginas, anoLote):
    i = int(i)
    final = paginas * i
    conn = ConexaoCSW.Conexao()
    start_time = time.time()

    itens = pd.read_sql('SELECT top '+str(final)+ ' ot.numeroOP, ot.codProduto , ot.codItem, ot.codSortimento, ot.seqTamanho , ot.qtdePecas1Qualidade, '
                        ' ot.qtdePecas2Qualidade , ot.qtdePecasImplementadas , op.situacao, op.codFaseAtual, op.codTipoOP, op.dataGeracao, op.codLote t WHERE t.codEmpresa = 1 and t.sequencia = i2.codSeqTamanho) as tamanho,'
                        ' op.codSeqRoteiroAtual  '
                        ' from tco.OrdemProdTamanhos ot '
                        ' join tco.OrdemProd op on op.codEmpresa = ot.codEmpresa and ot.numeroOP = op.numeroOP  '
                        " WHERE ot.codEmpresa = 1 and op.codLote  like '"+anoLote+"'",conn)
    end_time = time.time()
    execution_time = end_time - start_time
    execution_time = round(execution_time, 2)
    execution_time = str(execution_time)
    ConexaoCSW.ControleRequisicao('Consultar OPs Csw', execution_time, f'powerbi numero de intens {final}')





    inicial = (paginas - 1) * i
    itens = itens.iloc[inicial:final]

    return itens


