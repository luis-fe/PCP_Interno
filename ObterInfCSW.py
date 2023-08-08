import math
import time
import pandas as pd
import ConexaoCSW

def GetColecoes(pagina, itensPag,client_ip):
    conn = ConexaoCSW.Conexao()
    start_time = time.time()
    contagem = pd.read_sql("select COUNT(c.codcolecao) as cont from tcp.Colecoes c WHERE c.codEmpresa = 1 ", conn)
    pagina = int(pagina)
    itensPag = int(itensPag)
    totalPgs = contagem['cont'][0] /itensPag
    totalPgs = math.ceil(totalPgs)
    totalPgs = int(totalPgs)

    data = pd.read_sql("select codColecao , nome  from tcp.Colecoes c WHERE c.codEmpresa = 1 ",conn)
    conn.close()
    final = pagina * itensPag
    inicial = (pagina - 1) * itensPag

    data = data.iloc[inicial:final]

    data = {
        '0- Numerero de Paginas':totalPgs,
        '1- Detalhamento da Consulta:': data.to_dict(orient='records')
    }
    end_time = time.time()
    execution_time = end_time - start_time
    execution_time = round(execution_time, 2)
    execution_time = str(execution_time)
    ConexaoCSW.ControleRequisicao('Consultar Colecoes Csw', execution_time,client_ip)
    return [data]
def GetTipoNotas(pagina, itensPag,client_ip):
    conn = ConexaoCSW.Conexao()
    start_time = time.time()

    contagem = pd.read_sql("select COUNT(c.codigo) as cont from Fat.TipoDeNotaPadrao c ", conn)
    pagina = int(pagina)
    itensPag = int(itensPag)
    totalPgs = contagem['cont'][0] /itensPag
    totalPgs = math.ceil(totalPgs)
    totalPgs = int(totalPgs)

    data = pd.read_sql(" select t.codigo ,t.descricao  from Fat.TipoDeNotaPadrao t ",conn)
    conn.close()
    final = pagina * itensPag
    inicial = (pagina - 1) * itensPag

    data = data.iloc[inicial:final]

    data = {
        '0- Numerero de Paginas':totalPgs,
        '1- Detalhamento da Consulta:': data.to_dict(orient='records')
    }
    end_time = time.time()
    execution_time = end_time - start_time
    execution_time = round(execution_time, 2)
    execution_time = str(execution_time)
    ConexaoCSW.ControleRequisicao('Consultar tipoNotas Csw', execution_time, client_ip)
    return [data]

def GetLotesCadastrados(pagina, itensPag):
    conn = ConexaoCSW.Conexao()

    contagem = pd.read_sql("select COUNT(l.codLote) as cont   from tcl.Lote l "
                           " WHERE l.codEmpresa = 1 and l.descricao like '%PROJ%' OR l.descricao like '%PREV%'"
                           " order by l.codLote desc", conn)
    pagina = int(pagina)
    itensPag = int(itensPag)
    totalPgs = contagem['cont'][0] /itensPag
    totalPgs = math.ceil(totalPgs)
    totalPgs = int(totalPgs)

    data = pd.read_sql("select l.codLote , l.descricao  from tcl.Lote l"
                       " WHERE l.codEmpresa = 1 and l.descricao like '%PROJ%' OR l.descricao like '%PREV%'"
                       " order by l.codLote desc  ",conn)
    conn.close()
    final = pagina * itensPag
    inicial = (pagina - 1) * itensPag

    data = data.iloc[inicial:final]

    data = {
        '0- Numerero de Paginas':totalPgs,
        '1- Detalhamento da Consulta:': data.to_dict(orient='records')
    }
    print('novo')
    return [data]

