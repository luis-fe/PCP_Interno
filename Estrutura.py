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
                            " FROM tcp.CompVarSorGraTam cv "
                            "JOIN tcp.DadosGeraisEng d ON cv.codempresa = d.codEmpresa AND cv.codProduto = d.codEngenharia " 
                            " WHERE cv.codEmpresa = 1 AND d.codColecao in ("+ colecoes+")", conn)
    estrutura.rename(
        columns={'tipo': '01- tipo', "codColecao": '02- codColecao','codProduto':'03- codProduto'
                 ,'codSortimento':'04- codSortimento','tamanho':'05- tamanho','corProduto':'06- corProduto'
                 ,'codMP':'07- codMP','Tamanho':'08- TamanhoMP','nomeComponente':'09- nomeComponente','corComponente':'10- corComponente' ,'quantidade':'11- Consumo'},
        inplace=True)

    data = {
        '1- Detalhamento da Estutura:': estrutura.to_dict(orient='records')
    }

    return [data]
def EstruturaFiltroEngenharia(colecoes, Engenharia):
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
                            " FROM tcp.CompVarSorGraTam cv "
                            "JOIN tcp.DadosGeraisEng d ON cv.codempresa = d.codEmpresa AND cv.codProduto = d.codEngenharia " 
                            " WHERE cv.codEmpresa = 1 AND d.codColecao in ("+ colecoes+") and cv.codProduto in ("+Engenharia+")", conn)
    estrutura.rename(
        columns={'tipo': '01- tipo', "codColecao": '02- codColecao','codProduto':'03- codProduto'
                 ,'codSortimento':'04- codSortimento','tamanho':'05- tamanho','corProduto':'06- corProduto'
                 ,'codMP':'07- codMP','Tamanho':'08- TamanhoMP','nomeComponente':'09- nomeComponente','corComponente':'10- corComponente' ,'quantidade':'11- Consumo'},
        inplace=True)

    data = {
        '1- Detalhamento da Estutura:': estrutura.to_dict(orient='records')
    }

    return [data]
def EstruturaFiltroMateriaPrima(colecoes, codMP):
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
                            " FROM tcp.CompVarSorGraTam cv "
                            "JOIN tcp.DadosGeraisEng d ON cv.codempresa = d.codEmpresa AND cv.codProduto = d.codEngenharia " 
                            " WHERE cv.codEmpresa = 1 AND d.codColecao in ("+ colecoes+") and codMP in ("+codMP+")", conn)
    estrutura = pd.merge(estrutura, codMP, on='codMP')
    estrutura.rename(
        columns={'tipo': '01- tipo', "codColecao": '02- codColecao','codProduto':'03- codProduto'
                 ,'codSortimento':'04- codSortimento','tamanho':'05- tamanho','corProduto':'06- corProduto'
                 ,'codMP':'07- codMP','Tamanho':'08- TamanhoMP','nomeComponente':'09- nomeComponente','corComponente':'10- corComponente' ,'quantidade':'11- Consumo'},
        inplace=True)



    data = {
        '1- Detalhamento da Estutura:': estrutura.to_dict(orient='records')
    }

    return [data]




