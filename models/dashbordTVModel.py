import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL
import datetime
import pytz


def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.datetime.now(fuso_horario)
    hora_str = agora.strftime('%Y-%m-%d %H:%M:%S')
    dia = agora.strftime('%Y-%m-%d')
    return hora_str, dia

def Faturamento_ano(ano, empresa):
    datahora, dia = obterHoraAtual()


    conn = ConexaoCSW.Conexao()
    dataInicio = ano + '-01-01'
    dataFim = ano + '-12-31'

    query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codEmpresa = ' + empresa + ' and n.codPedido >= 0 ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 '

    dataframe = pd.read_sql(query, conn)

    meses = ['01-Janeiro', '02-Fevereiro', '03-Março', '04-Abril', '05-Maio', '06-Junho',
             '07-Julho', '08-Agosto', '09-Setembro', '10-Outubro', '11-Novembro', '12-Dezembro']

    faturamento_por_mes = []

    for mes in meses:
        # Filtrar os dados do mês atual
        procura = f"-{mes.split('-')[0]}-"
        df_mes = dataframe[dataframe['dataEmissao'].str.contains(procura)]

        # Calcular o faturamento do mês
        faturamento_mes = df_mes['faturado'].sum()
        faturamento_mes = "{:,.2f}".format(faturamento_mes)
        faturamento_mes = 'R$ ' + str(faturamento_mes)
        faturamento_mes = faturamento_mes.replace('.', ";")
        faturamento_mes = faturamento_mes.replace(',',".")
        faturamento_mes = faturamento_mes.replace(';', ",")
        faturamento_mes = faturamento_mes.replace('R$ 0,00', "")


        faturamento_por_mes.append(faturamento_mes)
    acumulado = 0
    faturamento_acumulado = []

    for mes in meses:

        procura = f"-{mes.split('-')[0]}-"
        df_mes = dataframe[dataframe['dataEmissao'].str.contains(procura)]
        acumulado = df_mes['faturado'].sum() + acumulado
        acumulado = "{:,.2f}".format(acumulado)
        faturamento_acumulado.append(acumulado)


    # Criar um DataFrame com os resultados
    df_faturamento = pd.DataFrame({'Mês': meses, 'Faturado': faturamento_por_mes, 'Acumulado':faturamento_acumulado})
    total = dataframe['faturado'].sum()
    total = "{:,.2f}".format(total)
    total = 'R$ ' + str(total)
    total = total.replace('.', ";")
    total = total.replace(',', ".")
    total = total.replace(';', ",")
    df_dia = dataframe[dataframe['dataEmissao'].str.contains(dia)]
    df_dia = df_dia['faturado'].sum()
    df_dia = "{:,.2f}".format(df_dia)
    df_dia = 'R$ ' + str(df_dia)
    df_dia = df_dia.replace('.', ";")
    df_dia = df_dia.replace(';', ",")

    data = {
        '1- Ano:': f'{ano}',
        '2- Empresa:': f'{empresa}',
        '3- No Retorna':"",
        '4- No Dia': f"{df_dia}",
        '5- TOTAL': f"{total}",
        '6- Atualizado as': f"{datahora}",
        '7- Detalhamento por Mes': df_faturamento.to_dict(orient='records')
    }
    return [data]


