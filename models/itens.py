# Importando os itens para o postgree, acionado via automacao diaria
import ConexaoCSW
import pandas as pd
def ItensCSW(dataIni, dataFim):
    conn = ConexaoCSW.Conexao()
    itens = pd.read_sql('SELECT i.codigo , i.nome, i2.codCor, i2.codSortimento, i2.codItemPai, i.dataInclusao'
                        ' (select t.descricao from tcp.Tamanhos t WHERE t.codEmpresa = 1 and t.sequencia = i2.codSeqTamanho) as tamanho '
                        ' FROM Cgi.Item i '
                        ' JOIN Cgi.Item2 i2 on i2.codItem = i.codigo '
                        " WHERE i.unidadeMedida = 'PC' and i2.Empresa = 1 and i2.codCor > 0",conn)
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
    itens.fillna('-', inplace=True)
    itens['dataInclusao'] = itens['dataInclusao'].str.replace('-', '2015-01-01')
    itens = itens.iloc[0:1000]

    return itens


def Categoria(contem, valorReferencia, valorNovo, categoria):
    if contem in valorReferencia:
        return valorNovo
    else:
        return categoria