import pandas as pd
import ConexaoCSW
# Constantes
SEM_ENGENHARIA = '0'
def Estrutura(colecoes, pagina=0 ,itensPag=0 , engenharia=SEM_ENGENHARIA, codMP = '0', nomecomponente ='0', Excel = False):
    nomeArquivo = f'EstruturaMP das Colecoes{colecoes}.csv'
    if pagina == 0 and engenharia==SEM_ENGENHARIA and nomecomponente =='0' and codMP =='0' and Excel == False:
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
                                " WHERE cv.codEmpresa = 1 AND d.codColecao in ("+ colecoes+") and cv.codProduto not like '03%' "
                                " union "
                                " select DISTINCT 'Padrao' as tipo, d.codColecao, c.codProduto, s.codSortimento , (select tm.descricao from tcp.Tamanhos tm WHERE tm.codEmpresa = t.Empresa  and tm.sequencia = t.codSeqTamanho) as tamanho, "
                                "s.corBase, "
                                " (select i2.codItemPai from  cgi.Item2  i2 WHERE  i2.Empresa = c.codEmpresa and i2.coditem = c.codComponente ) as codMP,"
                                " (select i2.codCor from  cgi.Item2  i2 WHERE  i2.Empresa = c.codEmpresa and i2.coditem = c.codComponente ) as corComponente, "
                                "(select tm.descricao from cgi.Item2  i2   "
                                " join tcp.Tamanhos tm on tm.CodEmpresa = i2.Empresa and tm.sequencia = i2.codseqtamanho where i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente) as Tamanho,"
                                " (select i.nome  from   cgi.item i WHERE  i.codigo = c.CodComponente ) as nomeComponente, c.quantidade from tcp.ComponentesPadroes c"
                                " join tcp.DadosGeraisEng d on c.codempresa = d.codEmpresa and c.codProduto = d.codEngenharia"
                                " join tcp.SortimentosProduto s on s.codEmpresa = c.codEmpresa and s.codProduto = c.codProduto "
                                " join tcp.IndEngenhariasPorSeqTam t on t.Empresa = c.codEmpresa and t.codEngenharia = c.codProduto "
                                " WHERE c.codEmpresa = 1 and d.codColecao in ("+ colecoes+") and t.codEngenharia not like '03%' ", conn)



        status = pd.read_sql("select e.codEngenharia as codProduto , e.status, d.codColecao  from tcp.Engenharia e "
                             " join tcp.DadosGeraisEng d on d.codEmpresa = e.codEmpresa and d.codEngenharia = e.codEngenharia  "
                             "where e.codEmpresa = 1 and e.status in (2,3) and d.codColecao in ("+ colecoes+")", conn)
        estrutura = pd.merge(estrutura, status, on='codProduto')
        estrutura.rename(
            columns={'tipo': '01- tipo', "codColecao": '02- codColecao','codProduto':'03- codProduto'
                     ,'codSortimento':'04- codSortimento','tamanho':'05- tamanho','corProduto':'06- corProduto'
                     ,'codMP':'07- codMP','Tamanho':'08- TamanhoMP','nomeComponente':'09- nomeComponente','corComponente':'10- corComponente' ,'quantidade':'11- Consumo'},
            inplace=True)
        estrutura["07- codMP"]=estrutura["07- codMP"].astype(str)
        estrutura = estrutura[~estrutura['07- codMP'].str.startswith('6')]
        estrutura.to_csv(nomeArquivo)
        data = {
            '1- Detalhamento da Estrutura:': estrutura.to_dict(orient='records')
            }
        print('novo')
        return [data]

    else:
        dataframe = pd.read_csv(nomeArquivo)
        dataframe["07- codMP"] = dataframe["07- codMP"].astype(str)

        #Aqui verifico se tem filtros
        dataframe = TemFiltro(engenharia,dataframe,'03- codProduto')
        dataframe = TemFiltro(codMP, dataframe, '07- codMP')
        dataframe = TemFiltro(nomecomponente, dataframe, '09- nomeComponente')

        # Aqui Verifico se tem paginamento
        estrutura = TemPaginamento(pagina,itensPag,dataframe)
        estrutura.fillna('-', inplace=True)

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
        print(coluna)
        return dataframe




