import pandas as pd
import ConexaoCSW
# Constantes
SEM_ENGENHARIA = '0'
def Estrutura(colecoes, pagina=0 ,itensPag=0 , engenharia=SEM_ENGENHARIA, codmp = '0'):
    nomeArquivo = f'EstruturaMP das Colecoes{colecoes}.csv'
    if pagina == 0 and engenharia==SEM_ENGENHARIA:
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


        estrutura.to_csv(nomeArquivo)
        data = {
            '1- Detalhamento da Estutura:': estrutura.to_dict(orient='records')
            }
        return [data]

    else:
        dataframe = pd.read_csv(nomeArquivo)

        #Aqui verifico se tem filtros
        dataframe = TemFiltro(engenharia,dataframe,'03- codProduto')
        dataframe = TemFiltro(codmp, dataframe, '04- codSortimento')

        # Aqui Verifico se tem paginamento
        estrutura = TemPaginamento(pagina,itensPag,dataframe)

        data = {'1- Detalhamento da Estrutura:': estrutura.to_dict(orient='records')}
        return [data]



def TemPaginamento(pagina, itensPag, dataframe):
    if pagina != 0:
        final = pagina * itensPag
        inicial = (pagina - 1) * itensPag
        estrutura = dataframe.iloc[inicial:final]

        return estrutura
    else:
        estrutura = dataframe
        return estrutura

def TemFiltro(nomedofiltro,dataframe, coluna):
    if nomedofiltro == '0':
        estrutura = dataframe
        return estrutura
    else:
        dataframe = dataframe[dataframe[coluna].str.contains(nomedofiltro)]
        dataframe = dataframe.reset_index(drop=True)
        return dataframe




