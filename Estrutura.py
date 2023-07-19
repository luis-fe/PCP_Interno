import pandas as pd
import ConexaoCSW

def Estrutura(colecoes):
    conn = ConexaoCSW.Conexao()
    estrutura = pd.read_sql("SELECT 'Variavel' AS tipo, d.codColecao, cv.codProduto, cv.codSortimento, " 
                            "(SELECT t.descricao FROM tcp.Tamanhos t WHERE t.codEmpresa = cv.codEmpresa AND t.sequencia = cv.seqTamanho) AS tamanho "  
                            "FROM tcp.CompVarSorGraTam cv JOIN tcp.DadosGeraisEng d ON cv.codempresa = d.codEmpresa AND cv.codProduto = d.codEngenharia " 
                            "WHERE cv.codEmpresa = 1 AND d.codColecao in ("+ colecoes+")", conn)
    return estrutura

x = Estrutura('1001,87')
print(x)


