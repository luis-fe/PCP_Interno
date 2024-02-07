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
import ConexaoPostgreMPL


def ResponsabilidadeFases():
    conn = ConexaoPostgreMPL.conexao()

    retorno = pd.read_sql('SELECT x.* FROM pcp."responsabilidadeFase" x ',conn)
    conn.close()

    return retorno

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

    justificativa = pd.read_sql('SELECT CONVERT(varchar(12), codop) as numeroOP, codfase as codFase, textolinha as justificativa FROM tco.ObservacoesGiroFasesTexto  t '
                                'WHERE empresa = 1 and textolinha is not null',conn)

    consulta['codFase'] = consulta['codFase'].astype(str)
    justificativa['codFase'] = justificativa['codFase'].astype(str)

    conn.close()  ## Conexao finalizada

    consulta = pd.merge(consulta,justificativa,on=['numeroOP','codFase'], how='left')

    responsabilidade = ResponsabilidadeFases()
    consulta = pd.merge(consulta,responsabilidade,on='codFase', how='left')


    consulta = consulta[consulta['data_entrada'] != '-']

    consulta.fillna('-', inplace=True)

    consulta['data_entrada'] = consulta['data_entrada'].str.slice(6, 10) + '-'+consulta['data_entrada'].str.slice(3, 5)+'-'+consulta['data_entrada'].str.slice(0, 2)
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
    consulta = consulta[consulta['dias na Fase'] != '']


    consulta = consulta.sort_values(by='dias na Fase', ascending=False)  # escolher como deseja classificar


    return consulta
