import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL
from datetime import datetime


### Nesse documento é realizado o processo de buscar as OPs em aberto para exibir em dashboard


#Passo 1: Buscando as OP's em aberto no csw:
def OPemProcesso(empresa):
    conn = ConexaoCSW.Conexao() # Conexao aberta do csw

    consulta = pd.read_sql(" SELECT op.codFaseAtual as codFase , op.numeroOP, op.codProduto,  "
                           "(select e.descricao from tcp.Engenharia e WHERE e.codempresa = op.codEmpresa and e.codengenharia = op.codProduto) as descricao "
                           "FROM tco.OrdemProd op  "
                           "where op.situacao = 3 and op.codempresa = "+"'"+empresa+"'",conn)

    consulta['codFase'] = consulta['codFase'].astype(str)

    faseAtual = pd.read_sql("SELECT numeroOP , codFase , r.nomeFase , case when SUBSTRING(observacao10,1,1) = 'I' then SUBSTRING(observacao10,17,11) else SUBSTRING(observacao10,14,11)"
                            'end  data_entrada '
                            'FROM tco.RoteiroOP r '
                            'Where codEmpresa =1 and numeroOP in ( '
                            'SELECT op.numeroOP  FROM tco.OrdemProd op '
                            "WHERE op.codEmpresa ="+"'"+ empresa+"' and op.situacao = 3)",conn)
    conn.close() ## Conexao finalizada

    faseAtual.fillna('-',inplace=True)
    faseAtual['codFase'] = faseAtual['codFase'].astype(str)

    faseAtual = faseAtual[faseAtual['data_entrada'] != '-']


    consulta = pd.merge(consulta,faseAtual,on=['numeroOP','codFase'],how='left')

    consulta['dias'] = pd.to_datetime(consulta['data_entrada'])
    # Obtendo a data de hoje
    data_de_hoje = datetime.today().date()
    consulta['data_string'] = pd.to_datetime(consulta['data_entrada'])
    consulta['diferenca_de_dias'] = data_de_hoje - consulta['data_string']


    return consulta