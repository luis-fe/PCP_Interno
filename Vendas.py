import ConexaoPostgreMPL
import ConexaoCSW
import pandas as pd


def TransformarPlanoTipoNota(plano):
    conn = ConexaoPostgreMPL.conexao()
    colecao = pd.read_sql('select colecao from pcp."colecoesPlano" where plano = %s', conn,params=(plano,))
    colecao = ', '.join(colecao['colecao'])
    conn.close()
    return colecao

def Projetado(plano):
    conn = ConexaoCSW.Conexao()
    projecao = pd.read_sql('select codEngenharia , (select tm.descricao from tcp.Tamanhos tm WHERE tm.codEmpresa = l.Empresa  and tm.sequencia = l.codSeqTamanho) as tamanho,'
                           '  (select s.corbase from tcp.SortimentosProduto s WHERE s.codEmpresa = l.Empresa and s.codProduto = l.codEngenharia  and s.codSortimento = l.codSortimento) as corProduto,'
                           ' l.qtdePecasImplementadas as projetado from tcl.LoteSeqTamanho l '
                           ' WHERE Empresa = 1 and l.codLote = %s ',conn,params=(lote,))
    return projecao

