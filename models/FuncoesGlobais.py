import math


def TemPaginamento(pagina, itensPag , dataframe , coluna_tamanho):
    if pagina != 0:
        totalPaginas = dataframe[coluna_tamanho].size/itensPag
        totalPaginas = math.ceil(totalPaginas)
        totalPaginas = int(totalPaginas)
        final = pagina * itensPag
        inicial = (pagina - 1) * itensPag
        estrutura = dataframe.iloc[inicial:final]


        return estrutura, totalPaginas
    else:
        estrutura = dataframe
        totalPaginas = dataframe[coluna_tamanho].size/itensPag
        totalPaginas = math.ceil(totalPaginas)
        totalPaginas = int(totalPaginas)

        return estrutura, totalPaginas

def TipagemDeVariavel(variavel,casasAposVirgula, prefixo='', posfixo =''):
    arredondamento = '{:,.'+casasAposVirgula+'f}'
    variavel = arredondamento.format(variavel)
    variavel = prefixo + str(variavel) + posfixo
    variavel = variavel.replace('.', ';')
    variavel = variavel.replace(',', '.')
    variavel = variavel.replace(';', ',')

    return variavel