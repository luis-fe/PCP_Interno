import math


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