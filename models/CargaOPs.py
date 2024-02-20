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
def OPemProcesso(empresa, AREA, filtro = '-'):

    if filtro == '-' or filtro == ''  :
        conn = ConexaoCSW.Conexao()  # Conexao aberta do CSW

        consulta = pd.read_sql("SELECT op.codTipoOP, op.codFaseAtual as codFase , op.numeroOP, op.codProduto, CASE WHEN SUBSTRING(observacao10, 1, 1) = 'I' THEN SUBSTRING(observacao10, 17, 11)  "
                               "ELSE SUBSTRING(observacao10, 14, 11) END data_entrada , r.nomeFase , "
                               "(select e.descricao from tcp.Engenharia e WHERE e.codempresa = op.codEmpresa and e.codengenharia = op.codProduto) as descricao FROM tco.OrdemProd op "
                               "inner join tco.RoteiroOP r on r.codempresa = op.codEmpresa and r.numeroop = op.numeroOP and op.codFaseAtual = r.codfase "
                               "where op.situacao = 3 and op.codempresa = '" + empresa + "'", conn)

        justificativa = pd.read_sql('SELECT CONVERT(varchar(12), codop) as numeroOP, codfase as codFase, textolinha as justificativa FROM tco.ObservacoesGiroFasesTexto  t '
                                    'having empresa = 1 and textolinha is not null',conn)
        justificativa['codFase'] = justificativa['codFase'].astype(str)


        conn2 = ConexaoPostgreMPL.conexao()
        justificativa2 = pd.read_sql('select ordemprod as "numeroOP", fase as "codFase", justificativa from "PCP".pcp.justificativa ',conn2)
        leadTime2 = pd.read_sql('select categoria, codfase as "codFase", leadtime as meta2, limite_atencao from "PCP".pcp.leadtime_categorias ',conn2)
        conn2.close()

        conn3 = ConexaoPostgreMPL.conexao2()

        pcs = pd.read_sql(
            'select numeroop as "numeroOP", sum(total_pcs) as "Qtd Pcs" from "Reposicao".off.ordemprod group by numeroop ',
            conn3)

        conn3.close()



        # Concatenar os DataFrames
        justificativa = pd.concat([justificativa, justificativa2], ignore_index=True)



        leadTime = pd.read_sql('SELECT f.codFase , f.leadTime as meta  FROM tcp.FasesProducao f WHERE f.codEmpresa = 1', conn)




        consulta['codFase'] = consulta['codFase'].astype(str)
        leadTime['codFase'] = leadTime['codFase'].astype(str)


        conn.close()  ## Conexao finalizada

        pcs.fillna(0, inplace=True)

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


        consulta['Area'] = consulta.apply(lambda row: 'PILOTO' if row['codTipoOP'] == 13 else 'PRODUCAO',axis=1 )









        consulta['categoria'] = '-'

        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CAMISA', row['descricao'], 'CAMISA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('POLO', row['descricao'], 'POLO', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('BATA', row['descricao'], 'CAMISA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('TRICOT', row['descricao'], 'TRICOT', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('BONE', row['descricao'], 'BONE', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CARTEIRA', row['descricao'], 'CARTEIRA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CAMISETA', row['descricao'], 'TSHIRT', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CAMISETA', row['descricao'], 'REGATA', row['categoria']), axis=1)


        consulta = pd.merge(consulta,leadTime2,on=['codFase','categoria'], how='left')
        consulta['meta2'].fillna(0, inplace=True)
        consulta['limite_atencao'].fillna(0, inplace=True)

        consulta['meta2'] = consulta['meta2'].astype(int)
        consulta['limite_atencao'] = consulta['limite_atencao'].astype(int)


        consulta['meta'] = consulta.apply(lambda row : row['meta'] if row['meta2'] == 0 else row['meta2'], axis=1)
        consulta.drop('meta2', axis=1, inplace=True)

        consulta['status'] = consulta.apply(lambda row: '⚠️atrasado' if row['dias na Fase'] > row['meta'] else 'normal',axis=1 )
        consulta['status'] = consulta.apply(lambda row: '⚠️atrasado' if row['status'] == '⚠️atrasado' and row['dias na Fase'] > row['limite_atencao']  else 'Atencao',axis=1 )

        consulta = consulta.sort_values(by=['status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        consulta['filtro'] = consulta['codProduto']+consulta['data_entrada']+consulta['categoria']+consulta['codFase']+'-'+consulta['nomeFase']+consulta['numeroOP']+consulta['responsavel']+consulta['status']
        consulta['filtro'] = consulta['filtro'].str.replace(' ', '')


        consulta.to_csv('cargaOP.csv',index=True)

        consulta = consulta[consulta['Area']== AREA]

        consulta.drop('filtro', axis=1, inplace=True)

        QtdPcs = consulta['Qtd Pcs'].sum()
        QtdPcs = "{:,.0f}".format(QtdPcs)
        QtdPcs = QtdPcs.replace(',','')

        totalOP = consulta['numeroOP'].count()
        totalOP = "{:,.0f}".format(totalOP)
        totalOP = totalOP.replace(',','')


        Atrazado = consulta[consulta['status'] == '⚠️atrasado']
        totalAtraso =Atrazado['numeroOP'].count()
        totalAtraso = "{:,.0f}".format(totalAtraso)
        totalAtraso = totalAtraso.replace(',','')


        dados = {
        '0-Total DE pçs':f'{QtdPcs} Pçs',
        '1-Total OP':f'{totalOP} Ops',
        '2- OPs Atrasadas':f'{totalAtraso} Ops',
        '3 -Detalhamento':consulta.to_dict(orient='records')

        }


        return pd.DataFrame([dados])
    else:
        filtros = pd.read_csv('cargaOP.csv')
        filtros = filtros[filtros['Area']== AREA]

        array = filtro.split(",")

        filtrosNovo = filtros[filtros['filtro'].str.contains(filtro)]
        if filtrosNovo.empty:

            dados = {
                '0-Total DE pçs': '',
                '1-Total OP': '',
                '2- OPs Atrasadas': '',
                '3 -Detalhamento': ''

            }

            return pd.DataFrame([dados])
        else:

            QtdPcs = filtrosNovo['Qtd Pcs'].sum()
            QtdPcs = "{:,.0f}".format(QtdPcs)
            QtdPcs = QtdPcs.replace(',', '')

            totalOP = filtrosNovo['numeroOP'].count()
            totalOP = "{:,.0f}".format(totalOP)
            totalOP = totalOP.replace(',', '')

            Atrazado = filtrosNovo[filtrosNovo['status'] == '⚠️atrasado']
            totalAtraso = Atrazado['numeroOP'].count()
            totalAtraso = "{:,.0f}".format(totalAtraso)
            totalAtraso = totalAtraso.replace(',', '')


            filtrosNovo.drop(['filtro','Unnamed: 0'], axis=1, inplace=True)

            dados = {
                '0-Total DE pçs': f'{QtdPcs} Pçs',
                '1-Total OP': f'{totalOP} Ops',
                '2- OPs Atrasadas': f'{totalAtraso} Ops',
                '3 -Detalhamento': filtrosNovo.to_dict(orient='records')

            }

            return pd.DataFrame([dados])




def getCategoriaFases():

    conn = ConexaoPostgreMPL.conexao()

    sql = pd.read_sql('select * from "PCP".pcp.leadtime_categorias ',conn)

    conn.close()

    return sql

def Categoria(contem, valorReferencia, valorNovo, categoria):
    if contem in valorReferencia:
        return valorNovo
    else:
        return categoria




