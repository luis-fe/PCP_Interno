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
def OPemProcesso(empresa, filtro = '-'):

    if filtro == '-' or filtro == ''  :
        conn = ConexaoCSW.Conexao()  # Conexao aberta do CSW

        consulta = pd.read_sql("SELECT op.codFaseAtual as codFase , op.numeroOP, op.codProduto, CASE WHEN SUBSTRING(observacao10, 1, 1) = 'I' THEN SUBSTRING(observacao10, 17, 11)  "
                               "ELSE SUBSTRING(observacao10, 14, 11) END data_entrada , r.nomeFase , "
                               "(select e.descricao from tcp.Engenharia e WHERE e.codempresa = op.codEmpresa and e.codengenharia = op.codProduto) as descricao FROM tco.OrdemProd op "
                               "inner join tco.RoteiroOP r on r.codempresa = op.codEmpresa and r.numeroop = op.numeroOP and op.codFaseAtual = r.codfase "
                               "WHERE op.situacao = 3 and op.codempresa = '" + empresa + "'", conn)

        justificativa = pd.read_sql('SELECT CONVERT(varchar(12), codop) as numeroOP, codfase as codFase, textolinha as justificativa FROM tco.ObservacoesGiroFasesTexto  t '
                                    'WHERE empresa = 1 and textolinha is not null',conn)


        leadTime = pd.read_sql('SELECT f.codFase , f.leadTime as meta  FROM tcp.FasesProducao f WHERE f.codEmpresa = 1', conn)

        pcs = pd.read_sql("SELECT t.numeroop, (sum(t.qtdePecas1Qualidade))as Qtd1 ,(sum(t.qtdePecas2Qualidade))as Qtd2  ,(sum(t.qtdePecasProgramadas))as prog "
                          "FROM tco.OrdemProdTamanhos t WHERE t.codempresa = "+empresa+" and t.numeroop in ( "
                          "SELECT numeroOP from tco.OrdemProd op WHERE op.codempresa = "+ empresa+" and op.numeroop = t.numeroOP and op.situacao = 3) group by numeroOP ", conn)


        consulta['codFase'] = consulta['codFase'].astype(str)
        leadTime['codFase'] = leadTime['codFase'].astype(str)

        justificativa['codFase'] = justificativa['codFase'].astype(str)

        conn.close()  ## Conexao finalizada

        pcs.fillna(0, inplace=True)

        pcs['Qtd Pcs'] = pcs.apply(lambda row : row['prog'] if row['Qtd1'] == 0 else row['Qtd1'] + row['Qtd2'], axis=1 )
        pcs.drop(['Qtd1','Qtd2','prog'], axis=1, inplace=True)
        consulta = pd.merge(consulta,pcs,on='numeroOP', how='left')


        consulta = pd.merge(consulta,justificativa,on=['numeroOP','codFase'], how='left')

        responsabilidade = ResponsabilidadeFases()
        consulta = pd.merge(consulta,responsabilidade,on='codFase', how='left')
        consulta = pd.merge(consulta,leadTime,on='codFase', how='left')


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



        consulta['status'] = consulta.apply(lambda row: '⚠️atrasado' if row['dias na Fase'] > row['meta'] else 'normal',axis=1 )
        consulta = consulta.sort_values(by=['status','dias na Fase'], ascending=False)  # escolher como deseja classificar



        consulta['filtro'] = consulta['codFase']+consulta['codProduto']+consulta['data_entrada']+consulta['descricao']+consulta['nomeFase']+consulta['numeroOP']+consulta['responsavel']+consulta['status']


        consulta.to_csv('cargaOP.csv',index=True)

        consulta.drop('filtro', axis=1, inplace=True)

        QtdPcs = consulta['Qtd Pcs'].sum()
        totalOP = consulta['numeroOP'].count()
        Atrazado = consulta[consulta['status'] == '⚠️atrasado']
        totalAtraso =Atrazado['numeroOP'].count()


        dados = {
        '0-Total DE pçs':f'{QtdPcs} Ops',
        '1-Total OP':f'{totalOP} Ops',
        '2- OPs Atrasadas':f'{totalAtraso} Ops',
        '3 -Detalhamento':consulta.to_dict(orient='records')

        }


        return pd.DataFrame([dados])
    else:
        filtros = pd.read_csv('cargaOP.csv')
        array = filtro.split(",")

        filtrosNovo = filtros[filtros['filtro'].str.contains(filtro)]
        if filtrosNovo.empty:
            print(filtrosNovo)

            dados = {
                '0-Total DE pçs': '',
                '1-Total OP': '',
                '2- OPs Atrasadas': '',
                '3 -Detalhamento': ''

            }

            return pd.DataFrame([dados])
        else:

            QtdPcs = filtrosNovo['Qtd Pcs'].sum()
            totalOP = filtrosNovo['numeroOP'].count()
            Atrazado = filtrosNovo[filtrosNovo['status'] == '⚠️atrasado']
            totalAtraso = Atrazado['numeroOP'].count()

            dados = {
                '0-Total DE pçs': f'{QtdPcs} Ops',
                '1-Total OP': f'{totalOP} Ops',
                '2- OPs Atrasadas': f'{totalAtraso} Ops',
                '3 -Detalhamento': filtrosNovo.to_dict(orient='records')

            }

            return pd.DataFrame([dados])









