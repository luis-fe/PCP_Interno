import pandas as pd
import ConexaoCSW
from datetime import datetime
import datetime
import pytz
import sys
import numpy
import time
import locale
import math


### Nesse documento é realizado o processo de buscar as OPs em aberto para exibir em dashboard
def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.datetime.now(fuso_horario)
    hora_str = agora.strftime('%Y-%m-%d %H:%M:%S')
    return hora_str



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
    consulta['data_entrada'] = pd.to_datetime(consulta['data_entrada'], errors='coerce')
    # Obtendo a data de hoje
    #data_de_hoje = pd.Timestamp.today().normalize()  # Convertendo para um objeto Timestamp do pandas

    # Verificando e lidando com valores nulos
    hora_str = obterHoraAtual()
    consulta['hora_str'] = hora_str
    consulta['hora_str'] = pd.to_datetime(consulta['hora_str'], errors='coerce')

    consulta['dias na Fase'] = (consulta['hora_str'] - consulta['data_entrada']).dt.days.fillna('')
    consulta['data_entrada'] = consulta['data_entrada'].astype(str)
    consulta.drop('hora_str', axis=1, inplace=True)
    #consulta['diferenca_de_dias'] = consulta['diferenca_de_dias'].astype(str)

    return consulta
