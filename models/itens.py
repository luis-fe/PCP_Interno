# Importando os itens para o postgree, acionado via automacao diaria
import ConexaoCSW
import pandas as pd
import time

def ItensCSW(i, paginas, orderby, data):
        i = int(i)
        final = paginas * i


        conn = ConexaoCSW.Conexao()
        start_time = time.time()

        itens = pd.read_sql('SELECT top '+str(final)+ ' i.codigo , i.nome, i2.codCor, i2.codSortimento, i2.codItemPai, i.dataInclusao, '
                            ' (select t.descricao from tcp.Tamanhos t WHERE t.codEmpresa = 1 and t.sequencia = i2.codSeqTamanho) as tamanho '
                            ' FROM Cgi.Item i '
                            ' JOIN Cgi.Item2 i2 on i2.codItem = i.codigo '
                            " WHERE (i.unidadeMedida = 'PC' or i.unidadeMedida = 'KIT' )and i2.Empresa = 1 "
                                                      "AND i2.codItemPai not like '25%'"
                                                      " and i2.codCor > 0 and dataInclusao is not null"
                                                      " and dataInclusao = '"+data+"' "
                                                 " order by dataInclusao "+orderby+"",conn)
        end_time = time.time()
        execution_time = end_time - start_time
        execution_time = round(execution_time, 2)
        execution_time = str(execution_time)
        ConexaoCSW.ControleRequisicao('Consultar itens Csw', execution_time, f'powerbi numero de intens {final}')



        itens['categoria'] = '-'
        itens['categoria'] = itens.apply(lambda row: Categoria('CAMISA', row['nome'], 'CAMISA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('TSHORT', row['nome'], 'CAMISETA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('POLO', row['nome'], 'POLO', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('BABY', row['nome'], 'CAMISETA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('REGATA', row['nome'], 'CAMISETA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('JUST', row['nome'], 'CAMISETA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('BATA', row['nome'], 'CAMISA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('JAQUETA', row['nome'], 'JAQUETA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('SHORT', row['nome'], 'BOARDSHORT', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('CARTEIRA', row['nome'], 'CARTEIRA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('MEIA', row['nome'], 'MEIA', row['categoria']),axis=1)
        itens['categoria'] = itens.apply(lambda row: Categoria('BLAZER', row['nome'], 'JAQUETA', row['categoria']),axis=1)
        itens.fillna('--', inplace=True)
        itens['dataInclusao'] = itens['dataInclusao'].str.replace('--', '2015-01-01')

        inicial = (paginas - 1) * i
        itens = itens.iloc[inicial:final]


        return itens




def Categoria(contem, valorReferencia, valorNovo, categoria):
    if contem in valorReferencia:
        return valorNovo
    else:
        return categoria