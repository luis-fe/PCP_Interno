import pandas as pd
from datetime import datetime
import ConexaoCSW
import ConexaoPostgreMPL


### Nesse documento é realizado o processo de buscar as OPs em aberto para exibir em dashboard

# Passo 1: Buscando as OP's em aberto no CSW
def OPemProcesso(empresa):
    conn = ConexaoCSW.Conexao()  # Conexao aberta do CSW

    consulta = pd.read_sql("SELECT op.codFaseAtual as codFase , op.numeroOP, op.codProduto, CASE WHEN SUBSTRING(observacao10, 1, 1) = 'I' THEN SUBSTRING(observacao10, 17, 11)  "
                           "ELSE SUBSTRING(observacao10, 14, 11) END data_entrada , r.nomeFase , "
                           "(select e.descricao from tcp.Engenharia e WHERE e.codempresa = op.codEmpresa and e.codengenharia = op.codProduto) as descricao FROM tco.OrdemProd op "
                           "inner join tco.RoteiroOP r on r.codempresa = op.codEmpresa and r.numeroop = op.numeroOP and op.codFaseAtual = r.codfase "
                           "WHERE op.situacao = 3 and op.codempresa = '" + empresa + "'", conn)

    consulta['codFase'] = consulta['codFase'].astype(str)

    conn.close()  ## Conexao finalizada

    consulta = consulta[consulta['data_entrada'] != '-']

    consulta.fillna('-', inplace=True)

    consulta['data_entrada'] = consulta['data_entrada']
    consulta['data_entrada'] = pd.to_datetime(consulta['data_entrada'],  errors='coerce')
    # Obtendo a data de hoje
    data_de_hoje = pd.Timestamp.today().normalize()  # Convertendo para um objeto Timestamp do pandas

    # Verificando e lidando com valores nulos
    consulta['diferenca_de_dias'] = (data_de_hoje - consulta['data_entrada']).dt.days.fillna('')
    consulta['data_entrada'] = consulta['data_entrada'].astype(str)
    #consulta.drop('data_entrada', axis=1, inplace=True)
    #consulta['diferenca_de_dias'] = consulta['diferenca_de_dias'].astype(str)

    return consulta
