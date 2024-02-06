import pandas as pd
from datetime import datetime
import ConexaoCSW
import ConexaoPostgreMPL


### Nesse documento é realizado o processo de buscar as OPs em aberto para exibir em dashboard

# Passo 1: Buscando as OP's em aberto no CSW
def OPemProcesso(empresa):
    conn = ConexaoCSW.Conexao()  # Conexao aberta do CSW

    consulta = pd.read_sql("SELECT op.codFaseAtual as codFase, op.numeroOP, op.codProduto, "
                           "(SELECT e.descricao FROM tcp.Engenharia e WHERE e.codempresa = op.codEmpresa and e.codengenharia = op.codProduto) as descricao "
                           "FROM tco.OrdemProd op "
                           "WHERE op.situacao = 3 and op.codempresa = '" + empresa + "'", conn)

    consulta['codFase'] = consulta['codFase'].astype(str)

    faseAtual = pd.read_sql("SELECT numeroOP, codFase, r.nomeFase, "
                            "CASE WHEN SUBSTRING(observacao10, 1, 1) = 'I' THEN SUBSTRING(observacao10, 17, 11) "
                            "ELSE SUBSTRING(observacao10, 14, 11) END data_entrada "
                            "FROM tco.RoteiroOP r "
                            "WHERE codEmpresa = 1 AND numeroOP IN ("
                            "SELECT op.numeroOP FROM tco.OrdemProd op "
                            "WHERE op.codEmpresa = '" + empresa + "' AND op.situacao = 3)", conn)

    conn.close()  ## Conexao finalizada

    faseAtual.fillna('-', inplace=True)
    faseAtual['codFase'] = faseAtual['codFase'].astype(str)

    faseAtual = faseAtual[faseAtual['data_entrada'] != '-']

    consulta = pd.merge(consulta, faseAtual, on=['numeroOP', 'codFase'], how='left')
    consulta.fillna('-', inplace=True)
    consulta['data_entrada'] =consulta[consulta['data_entrada'] != '-']

    consulta['data_entrada'] = pd.to_datetime(consulta['data_entrada'])
    # Obtendo a data de hoje
    data_de_hoje = pd.Timestamp.today().normalize()  # Convertendo para um objeto Timestamp do pandas

    # Verificando e lidando com valores nulos
    consulta['diferenca_de_dias'] = (data_de_hoje - consulta['data_entrada']).dt.days.fillna('')
    consulta.drop('data_entrada', axis=1, inplace=True)
    consulta['diferenca_de_dias'] = consulta['diferenca_de_dias'].astype(str)

    return consulta
