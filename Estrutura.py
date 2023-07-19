import pandas as pd
import ConexaoCSW

def Estrutura(colecoes):
    conn = ConexaoCSW.Conexao()
    estrutura = pd.read_sql("SELECT 'Variavel' AS tipo, d.codColecao, cv.codProduto, cv.codSortimento, " 
                            "(SELECT t.descricao FROM tcp.Tamanhos t WHERE t.codEmpresa = cv.codEmpresa AND t.sequencia = cv.seqTamanho) AS tamanho, "
                            "(select s.corbase from tcp.SortimentosProduto s WHERE s.codEmpresa = cv.codEmpresa and s.codProduto = cv.codProduto and s.codSortimento = cv.codSortimento) as corProduto,"
                            " (select i2.codItemPai from  tcp.ComponentesVariaveis c join cgi.Item2  i2 on i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as codMP,"
                            " (select i2.codCor from  tcp.ComponentesVariaveis c "
	                        " join cgi.Item2  i2 on i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as corComponente,"
                            " (select t.descricao from  tcp.ComponentesVariaveis c "
	                        " join cgi.Item2  i2   on i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente join tcp.Tamanhos t on t.CodEmpresa = i2.Empresa and t.sequencia = i2.codseqtamanho"
		                    " WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as Tamanho,"
                            " (select i.nome  from   tcp.ComponentesVariaveis c join cgi.item i on i.codigo = c.CodComponente WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as nomeComponente, "
                            "cv.quantidade "  
                            " FROM tcp.CompVarSorGraTam cv JOIN tcp.DadosGeraisEng d ON cv.codempresa = d.codEmpresa AND cv.codProduto = d.codEngenharia " 
                            " WHERE cv.codEmpresa = 1 AND d.codColecao in ("+ colecoes+")", conn)
    estrutura.rename(
        columns={'tipo': '1- tipo', "codColecao": '2- codColecao','codProduto':'3- codProduto'
                 ,'codSortimento':'4- codSortimento','tamanho':'5- tamanho','corProduto':'6- corProduto'},
        inplace=True)

    data = {
        '1- Detalhamento da Estutura:': estrutura.to_dict(orient='records')
    }

    return [data]





