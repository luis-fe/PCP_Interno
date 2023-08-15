import math
import time
import pandas as pd
from models import ConexaoCSW, ConexaoPostgreMPL

# Constantes
SEM_ENGENHARIA = '0'

def TransformarPlanoColecao(plano):
    conn = ConexaoPostgreMPL.conexao()
    colecao = pd.read_sql('select colecao from pcp."colecoesPlano" where plano = %s', conn,params=(plano,))
    colecao = ', '.join(colecao['colecao'])
    conn.close()
    return colecao


def Estrutura(client_ip,plano, pagina=0 ,itensPag=0 , engenharia=SEM_ENGENHARIA, codMP = '0', nomecomponente ='0', Excel = False, tamProduto ='0', fornecedor = '0', desceng ='0'):
    colecoes = TransformarPlanoColecao(plano)
    nomeArquivo = f'EstruturaMP das Colecoes{colecoes}.csv'
    if pagina == 0 and engenharia==SEM_ENGENHARIA and nomecomponente =='0' and codMP =='0' and Excel == False and tamProduto == '0' and fornecedor == '0' and desceng =='0':
        conn = ConexaoCSW.Conexao()
        start_time = time.time()

        estrutura = pd.read_sql("SELECT now() as dia, 'Variavel' AS tipo, d.codColecao, cv.codProduto, cv.codSortimento, " 
                                "(SELECT t.descricao FROM tcp.Tamanhos t WHERE t.codEmpresa = cv.codEmpresa AND t.sequencia = cv.seqTamanho) AS tamanho, "
                                "(select s.corbase from tcp.SortimentosProduto s WHERE s.codEmpresa = cv.codEmpresa and s.codProduto = cv.codProduto and s.codSortimento = cv.codSortimento) as corProduto,"
                                " (select s.situacao from tcp.SortimentosProduto s WHERE s.codEmpresa = cv.codEmpresa and s.codProduto = cv.codProduto and s.codSortimento = cv.codSortimento) as situacao,"
                                " (select i2.codItemPai from  tcp.ComponentesVariaveis c join cgi.Item2  i2 on i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as codMP,"
                                " (select i2.codCor from  tcp.ComponentesVariaveis c "
                                " join cgi.Item2  i2 on i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as corComponente,"
                                " (select t.descricao from  tcp.ComponentesVariaveis c "
                                " join cgi.Item2  i2   on i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente join tcp.Tamanhos t on t.CodEmpresa = i2.Empresa and t.sequencia = i2.codseqtamanho"
                                " WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as Tamanho,"
                                " (select i.nome  from   tcp.ComponentesVariaveis c join cgi.item i on i.codigo = c.CodComponente WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as nomeComponente, "
                                "cv.quantidade,"
                                " (select i2.coditem from  tcp.ComponentesVariaveis c join cgi.Item2  i2 on i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente WHERE  cv.codEmpresa = c.codEmpresa and cv.codProduto = c.codProduto and cv.sequencia = c.codSequencia ) as codreduzido "
                                " FROM tcp.CompVarSorGraTam cv "
                                "JOIN tcp.DadosGeraisEng d ON cv.codempresa = d.codEmpresa AND cv.codProduto = d.codEngenharia " 
                                " WHERE cv.codEmpresa = 1 AND d.codColecao in ("+ colecoes+") and cv.codProduto not like '03%' "
                                " union "
                                " select DISTINCT now() as dia, 'Padrao' as tipo, d.codColecao, c.codProduto, s.codSortimento , (select tm.descricao from tcp.Tamanhos tm WHERE tm.codEmpresa = t.Empresa  and tm.sequencia = t.codSeqTamanho) as tamanho, "
                                "s.corBase, s.situacao, "
                                " (select i2.codItemPai from  cgi.Item2  i2 WHERE  i2.Empresa = c.codEmpresa and i2.coditem = c.codComponente ) as codMP,"
                                " (select i2.codCor from  cgi.Item2  i2 WHERE  i2.Empresa = c.codEmpresa and i2.coditem = c.codComponente ) as corComponente, "
                                "(select tm.descricao from cgi.Item2  i2   "
                                " join tcp.Tamanhos tm on tm.CodEmpresa = i2.Empresa and tm.sequencia = i2.codseqtamanho where i2.Empresa = c.codEmpresa and i2.coditem = c.CodComponente) as Tamanho,"
                                " (select i.nome  from   cgi.item i WHERE  i.codigo = c.CodComponente ) as nomeComponente, c.quantidade, "
                                " (select i2.codItem from  cgi.Item2  i2 WHERE  i2.Empresa = c.codEmpresa and i2.coditem = c.codComponente ) as codreduzido"
                                " from tcp.ComponentesPadroes c"
                                " join tcp.DadosGeraisEng d on c.codempresa = d.codEmpresa and c.codProduto = d.codEngenharia"
                                " join tcp.SortimentosProduto s on s.codEmpresa = c.codEmpresa and s.codProduto = c.codProduto "
                                " join tcp.IndEngenhariasPorSeqTam t on t.Empresa = c.codEmpresa and t.codEngenharia = c.codProduto "
                                " WHERE c.codEmpresa = 1 and d.codColecao in ("+ colecoes+") and t.codEngenharia not like '03%' ", conn)

        estrutura['situacao'] = estrutura.apply(lambda row: '1-Ativo' if row['situacao'] == 1
                                                                        else '0-Inativo', axis=1)
        status = pd.read_sql("select e.codEngenharia as codProduto , e.status, e.descricao as descricaoeng  from tcp.Engenharia e "
                             " join tcp.DadosGeraisEng d on d.codEmpresa = e.codEmpresa and d.codEngenharia = e.codEngenharia  "
                             "where e.codEmpresa = 1 and e.status in (2,3) and d.codColecao in ("+ colecoes+")", conn)

        fornecedorPref = pd.read_sql("select codItem as codreduzido, codFornecedor  FROM cgi.FornecHomologados fh "
                                     "WHERE fh.codEmpresa = 1 and fh.fornecedorPreferencial = 1 ", conn)
        fornecedorPref['codreduzido'] =fornecedorPref['codreduzido'].astype(str)
        descricaoFornecdor = pd.read_sql("select DISTINCT f.codFornecedor, f.nomeFornecedor  from cgi.FornecHomologados f "
                                        "WHERE f.codEmpresa = 1 ", conn)

        fornecedorPref = pd.merge(fornecedorPref,descricaoFornecdor,on='codFornecedor')

        conn.close()
        estrutura = pd.merge(estrutura, status, on='codProduto')
        estrutura = pd.merge(estrutura, fornecedorPref, on='codreduzido', how='left')
        estrutura.drop('codFornecedor', axis=1, inplace=True)
        estrutura.drop('codreduzido', axis=1, inplace=True)
        estrutura.rename(
            columns={'tipo': '01- tipo', "codColecao": '02- codColecao','codProduto':'03- codProduto'
                     ,'codSortimento':'04- codSortimento','tamanho':'05- tamanho','corProduto':'06- corProduto'
                     ,'codMP':'07- codMP','Tamanho':'08- TamanhoMP','nomeComponente':'09- nomeComponente','corComponente':'10- corComponente' ,'quantidade':'11- Consumo'
                     ,"nomeFornecedor":"12-nomeFornecedor","status":"13-statusEng","situacao":"14- situacao cor","descricaoeng":"15- descricao Produto"},
            inplace=True)
        estrutura["07- codMP"] = estrutura["07- codMP"].astype(str)
        estrutura = estrutura[~estrutura['07- codMP'].str.startswith('6')]
        estrutura.fillna('-', inplace=True)
        estrutura['12-nomeFornecedor'] = estrutura.apply(lambda row: TratamentoNomeFornecedor(row['12-nomeFornecedor'], 'MPL IND', 'MPL TEXTIL'), axis=1)
        estrutura['12-nomeFornecedor'] = estrutura.apply(lambda row: TratamentoNomeFornecedor(row['12-nomeFornecedor'], 'MENEGOTTI', 'MENEGOTTI'), axis=1)
        estrutura['12-nomeFornecedor'] = estrutura.apply(lambda row: TratamentoNomeFornecedor(row['12-nomeFornecedor'], 'RVB', 'RVB'), axis=1)
        estrutura['12-nomeFornecedor'] = estrutura.apply(lambda row: TratamentoNomeFornecedor(row['12-nomeFornecedor'], 'DALILA', 'DALILA'), axis=1)
        estrutura['12-nomeFornecedor'] = estrutura.apply(lambda row: TratamentoNomeFornecedor(row['12-nomeFornecedor'], 'CONE SUL', 'CONE SUL'), axis=1)
        estrutura['12-nomeFornecedor'] = estrutura.apply(lambda row: TratamentoNomeFornecedor(row['12-nomeFornecedor'], 'EXCIM', 'EXCIM'), axis=1)
        estrutura['12-nomeFornecedor'] = estrutura.apply(lambda row: TratamentoNomeFornecedor(row['12-nomeFornecedor'], 'ADAR I', 'ADAR'), axis=1)
        estrutura = estrutura.reset_index(drop=True)
        estrutura.to_csv(nomeArquivo)

        data = {
            '1- Detalhamento da Estrutura:': estrutura.to_dict(orient='records')
            }
        end_time = time.time()
        execution_time = end_time - start_time
        execution_time = round(execution_time, 2)
        execution_time = str(execution_time)

        ConexaoCSW.ControleRequisicao('Consultar Estrutura Csw', execution_time, client_ip)
        return [data]

    else:

        dataframe = pd.read_csv(nomeArquivo)
        dataframe["07- codMP"] = dataframe["07- codMP"].astype(str)

        #Aqui verifico se tem filtros
        dataframe = TemFiltro(engenharia,dataframe,'03- codProduto')
        dataframe = TemFiltro(codMP, dataframe, '07- codMP')
        dataframe = TemFiltro(nomecomponente.upper(), dataframe, '09- nomeComponente')
        dataframe = TemFiltro(tamProduto.upper(), dataframe, '05- tamanho')
        dataframe = TemFiltro(fornecedor.upper(), dataframe, '12-nomeFornecedor')
        dataframe = TemFiltro(desceng.upper(), dataframe, '15- descricao Produto')


        # Aqui Verifico se tem paginamento
        estrutura, totalPg = TemPaginamento(pagina,itensPag,dataframe)
        estrutura.fillna('-', inplace=True)
        if  totalPg == False:
            data = {'1- Detalhamento da Estrutura:': estrutura.to_dict(orient='records')}
            return [data]
        else:
            data = {'1- Detalhamento da Estrutura:': estrutura.to_dict(orient='records'),
                    '0- ToalPg':f'{totalPg}'}
            return [data]


def TemPaginamento(pagina, itensPag, dataframe):
    if pagina != 0:
        totalPaginas = dataframe['03- codProduto'].size/itensPag
        totalPaginas = math.ceil(totalPaginas)
        totalPaginas = int(totalPaginas)
        final = pagina * itensPag
        inicial = (pagina - 1) * itensPag
        estrutura = dataframe.iloc[inicial:final]


        return estrutura, totalPaginas
    else:
        estrutura = dataframe
        return estrutura, False

def TemFiltro(nomedofiltro,dataframe, coluna):
    if nomedofiltro == '0':
        estrutura = dataframe
        return estrutura
    else:
        dataframe = dataframe[dataframe[coluna].str.contains(nomedofiltro)]
        dataframe = dataframe.reset_index(drop=True)
        print(coluna)
        return dataframe


def TratamentoNomeFornecedor(nomeAntigo, contem, retorno):
    if contem in nomeAntigo:
        return retorno
    else:
        return nomeAntigo
