import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL
import datetime
import pytz
import locale


def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.datetime.now(fuso_horario)
    hora_str = agora.strftime('%Y-%m-%d %H:%M:%S')
    dia = agora.strftime('%Y-%m-%d')
    return hora_str, dia

def obter_notaCsw():
    conn = ConexaoCSW.Conexao()
    data = pd.read_sql(" select t.codigo ,t.descricao  from Fat.TipoDeNotaPadrao t ", conn)
    conn.close()

    return data
def Faturamento_ano(ano, empresa):
    datahora, dia = obterHoraAtual()
    tipoNota = obter_notaCsw()

    tipoNotaConsiderar = ConfTipoNota(empresa)



    conn = ConexaoCSW.Conexao()
    mesFinal, mesAtual = EncontrandoMesAtual()
    dataInicio = ano + '-'+mesAtual+'-01'
    dataFim = ano + '-12-31'

    if empresa == 'Todas':
        query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codPedido >= 0 ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 ' \
                                                            ' union ' \
                                                            'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codTipoDeNota in (30, 180, 156, 51, 175, 81, 12, 47, 67, 149, 159, 1030, 2015, 1, 27, 102, 2, 9998) and codPedido is null ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 ' \


        retornaCsw = pd.read_sql(
        "SELECT  i.codPedido, e.vlrSugestao, sum(i.qtdePecasConf) as conf , sum(i.qtdeSugerida) as qtde,  i.codSequencia,  "
        " (SELECT codTipoNota  FROM ped.Pedido p WHERE p.codEmpresa = i.codEmpresa and p.codpedido = i.codPedido) as codigo "
        " FROM ped.SugestaoPed e "
        " inner join ped.SugestaoPedItem i on i.codEmpresa = e.codEmpresa and i.codPedido = e.codPedido and  i.codSequencia= e.codSequencia "
        ' WHERE'
        " e.dataGeracao > '2023-01-01' and situacaoSugestao = 2"
        " group by i.codPedido, e.vlrSugestao,  i.codSequencia ", conn)
    elif empresa == 'Varejo':
        query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado ' \
                'FROM Fat.NotaFiscal n ' \
                'where n.codPedido >= 0 ' \
                'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
                                                                   'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2  and codempresa in (100, 101)'
        retornaCsw = pd.read_sql(
        "SELECT  i.codPedido, e.vlrSugestao, sum(i.qtdePecasConf) as conf , sum(i.qtdeSugerida) as qtde,  i.codSequencia,  "
        " (SELECT codTipoNota  FROM ped.Pedido p WHERE p.codEmpresa = i.codEmpresa and p.codpedido = i.codPedido) as codigo "
        " FROM ped.SugestaoPed e "
        " inner join ped.SugestaoPedItem i on i.codEmpresa = e.codEmpresa and i.codPedido = e.codPedido "
        ' WHERE e.codEmpresa in (100, 101)'
        " and e.dataGeracao > '2023-01-01' and situacaoSugestao = 2"
        " group by i.codPedido, e.vlrSugestao,  i.codSequencia ", conn)



    else:
        query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, codPedido, codNumNota, codEmpresa  ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codPedido >= 0 '   \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 and codempresa ='+ "'" + empresa + "'" \
                                                            ' union ' \
                                                            "select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, '0' ,codNumNota, "+"'"+empresa+"'" \
            ' FROM Fat.NotaFiscal n ' \
            'where n.codTipoDeNota in (30, 180, 156, 51, 175, 81, 12, 47, 67, 149, 159, 1030, 2015, 1, 27, 102, 2, 9998) and codPedido is null ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 and codempresa ='+ "'" + empresa + "'" \

        retornaCsw = pd.read_sql(
        "SELECT  i.codPedido, e.vlrSugestao, sum(i.qtdePecasConf) as conf , sum(i.qtdeSugerida) as qtde,  i.codSequencia,  "
        " (SELECT codTipoNota  FROM ped.Pedido p WHERE p.codEmpresa = i.codEmpresa and p.codpedido = i.codPedido) as codigo "
        " FROM ped.SugestaoPed e "
        " inner join ped.SugestaoPedItem i on i.codEmpresa = e.codEmpresa and i.codPedido = e.codPedido "
        ' WHERE e.codEmpresa =' + empresa +
        " and e.dataGeracao > '2023-01-01' and situacaoSugestao = 2"
        " group by i.codPedido, e.vlrSugestao,  i.codSequencia ", conn)





    tipoNota['codigo'] = tipoNota['codigo'].astype(str)
    retornaCsw = pd.merge(retornaCsw, tipoNota, on='codigo')

    retornaCsw["codPedido"] = retornaCsw["codPedido"] + '-' + retornaCsw["codSequencia"]

    # Retirando as bonificacoes
    retornaCswSB = retornaCsw[retornaCsw['codigo'] != 39]
    retornaCswMPLUS = retornaCsw[retornaCsw['codigo'] == 39]

    retornaCswSB = retornaCswSB[retornaCswSB['conf'] == 0]
    retornaCswMPLUS = retornaCswMPLUS[retornaCswMPLUS['conf'] == 0]

    retorna = retornaCswSB['vlrSugestao'].sum()
    retorna = "{:,.2f}".format(retorna)
    retorna = str(retorna)
    retorna = 'R$ ' + retorna.replace(',', ';').replace('.', ',').replace(';', '.')

    ValorRetornaMplus = retornaCswMPLUS['vlrSugestao'].sum()
    ValorRetornaMplus = "{:,.2f}".format(ValorRetornaMplus)
    ValorRetornaMplus = str(ValorRetornaMplus)
    ValorRetornaMplus = 'R$ ' + ValorRetornaMplus.replace(',', ';').replace('.', ',').replace(';', '.')

    dataframe = pd.read_sql(query, conn)
    nome = ano + 'Vendas'+empresa+'.csv'
    dataframe2 = pd.read_csv(nome)

    dataframe = pd.concat([dataframe,dataframe2],ignore_index=True)

    #dataframe.to_csv('teste.csv')
    dataframe['tiponota'] =dataframe['tiponota'].astype(str)
    dataframe = pd.merge(dataframe, tipoNotaConsiderar, on='tiponota')


    meses = ['01-Janeiro', '02-Fevereiro', '03-Março', '04-Abril', '05-Maio', '06-Junho',
             '07-Julho', '08-Agosto', '09-Setembro', '10-Outubro', '11-Novembro', '12-Dezembro']

    faturamento_por_mes = []
    acumulado = 0.00
    faturamento_acumulado = []

    for mes in meses:
        # Filtrar os dados do mês atual
        procura = f"-{mes.split('-')[0]}-"
        df_mes = dataframe[dataframe['dataEmissao'].str.contains(procura)]

        # Calcular o faturamento do mês
        faturamento_mes = df_mes['faturado'].sum()

        # Acumular o faturamento
        acumulado += faturamento_mes

        # Formatar o faturamento do mês
        faturamento_mes = "{:,.2f}".format(faturamento_mes)
        faturamento_mes = 'R$ ' + faturamento_mes.replace(',', ';').replace('.', ',').replace(';', '.')
        if faturamento_mes == 'R$ 0,00':
            faturamento_mes = ''

        # Formatar o acumulado
        acumulado_str = "{:,.2f}".format(acumulado)
        acumulado_str = 'R$ ' + acumulado_str.replace('.', ';')

        acumulado_str = acumulado_str.replace(',', '.')
        acumulado_str = acumulado_str.replace(';', ',')

        faturamento_por_mes.append(faturamento_mes)
        faturamento_acumulado.append(acumulado_str)

    # Criar um DataFrame com os resultados
    df_faturamento = pd.DataFrame({'Mês': meses, 'Faturado': faturamento_por_mes, 'Fat.Acumulado':faturamento_acumulado})
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
    df_dia = df_dia.replace(',', ".")
    df_dia = df_dia.replace(';', ",")

    metaMes, metaTotal = GetMetas(empresa, ano)
    metaTotal = "{:,.2f}".format(metaTotal)
    metaTotal = 'R$ ' + str(metaTotal)
    metaTotal = metaTotal.replace('.', ";")
    metaTotal = metaTotal.replace(',', ".")
    metaTotal = metaTotal.replace(';', ",")

    df_faturamento['meses']= df_faturamento['Mês']

    df_faturamento = pd.merge(df_faturamento, metaMes, on="meses", how='left')
    df_faturamento.drop('meses', axis=1, inplace=True)
    df_faturamento.drop('Mês_x', axis=1, inplace=True)
    df_faturamento['Mês']= df_faturamento['Mês_y']
    df_faturamento.drop('Mês_y', axis=1, inplace=True)


    def format_with_separator(value):
        return locale.format('%0.2f', value, grouping=True)



    df_faturamento['meta'] = df_faturamento['meta'].apply(format_with_separator)


    df_faturamento['meta acum.'] = df_faturamento['meta acum.'].apply(format_with_separator)
    df_faturamento['meta'] = df_faturamento['meta'].astype(str)
    df_faturamento['meta acum.'] = df_faturamento['meta acum.'].astype(str)

    df_faturamento['meta'] = df_faturamento['meta'].str.replace(',', ';')
    df_faturamento['meta acum.'] = df_faturamento['meta acum.'].str.replace(',', ';')

    df_faturamento['meta'] = df_faturamento['meta'].str.replace('.', ',')
    df_faturamento['meta acum.'] = df_faturamento['meta acum.'].str.replace('.', ',')

    df_faturamento['meta'] = 'R$ '+df_faturamento['meta'].str.replace(';', '.')
    df_faturamento['meta acum.'] = 'R$ ' + df_faturamento['meta acum.'].str.replace(';', '.')
    df_faturamento['Mês'] = df_faturamento['Mês'].str.split('-', 1).str[1]
    df_faturamento = df_faturamento.append({'Mês': '✈TOTAL','meta':metaTotal, 'Faturado':total,'meta acum.':metaTotal,'Fat.Acumulado':total}, ignore_index=True)
    df_faturamento.fillna('-',inplace=True)

    if empresa == 'Todas':
        data = {
            '1- Ano:': f'{ano}',
            '2- Empresa:': f'{empresa}',
            '3- No Retorna': f"{retorna}",
            '3.1- Retorna Mplus': f"{ValorRetornaMplus}",
            '4- No Dia': f"{df_dia}",
            '5- TOTAL': f"{total}",
            '6- Atualizado as': f"{datahora}",
            '7- Detalhamento por Mes': df_faturamento.to_dict(orient='records')
        }
    else:
        data = {
        '1- Ano:': f'{ano}',
        '2- Empresa:': f'{empresa}',
        '3- No Retorna':f"{retorna}",
        '3.1- Retorna Mplus': f"{ValorRetornaMplus}",
        '4- No Dia': f"{df_dia}",
        '5- TOTAL': f"{total}",
        '6- Atualizado as': f"{datahora}",
        '7- Detalhamento por Mes': df_faturamento.to_dict(orient='records')
    }
    return [data]

def GetMetas(empresa, ano):
    conn = ConexaoPostgreMPL.conexao()
    if empresa != 'Todas':
        consulta = pd.read_sql('select mes as "Mês", meta from "PCP"."DashbordTV".metas '
                           "where empresa = %s and ano = %s   order by mes " , conn, params=(empresa,ano))
    else:
        consulta = pd.read_sql('select mes as "Mês", meta from "PCP"."DashbordTV".metas '
                           "where ano = %s and  empresa <> 'Varejo' order by mes" , conn, params=(ano,))
        consulta = consulta.groupby('Mês').agg({
            'Mês': 'first',
            'meta':'sum'

        })

    consulta['meta acum.'] = consulta['meta'].cumsum()

    conn.close()
    consulta.fillna('-',inplace=True)
    metaTotal = consulta['meta'].sum()
    consulta['meses'] = consulta['Mês']


    return consulta, metaTotal

def ConfTipoNota(empresa):
    conn = ConexaoPostgreMPL.conexao()

    if empresa == 'Todas':
        consulta = pd.read_sql('select distinct tiponota from "DashbordTV".configuracao c  '
                           "where c.exibi_todas_empresas = 'sim'  ",conn)

    elif empresa == 'Varejo':
        consulta = pd.read_sql('select distinct tiponota from "DashbordTV".configuracao c  '
                           "where c.empresa = 'Varejo' ",conn)
    elif empresa == 'Outras':
        consulta = pd.read_sql('select distinct tiponota from "DashbordTV".configuracao c  '
                           "where c.empresa = 'Outras' ",conn)



    else:
        consulta = pd.read_sql('select tiponota from "DashbordTV".configuracao c '
                           "where c.empresa = %s  ",conn, params=(empresa))

    consulta['tiponota']= consulta['tiponota'].astype(str)


    return consulta

def EncontrandoMesAtual():
    datahora, dia = obterHoraAtual()
    mes = dia[5:7]

    if mes == '01':
        return '01' ,'01'

    else:
        mesAtual = int(mes)
        mesFinal = mesAtual - 1
        mesFinal = str(mesFinal)

        return mesFinal , mes

def Backup(ano, empresa):
    datahora, dia = obterHoraAtual()

    mesFinal, mesAtual = EncontrandoMesAtual()



    conn = ConexaoCSW.Conexao()
    dataInicio = ano + '-01-01'
    if mesFinal in ['11','04','06','09']:
        dataFim = ano + '-'+mesFinal+'-30'
    elif mesFinal in ['02']:
        dataFim = ano + '-' + mesFinal + '-28'
    else:
        dataFim = ano + '-'+mesFinal+'-31'

    if empresa == 'Todas':


        query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, codPedido ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codPedido >= 0 ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 ' \
                                                            ' union ' \
                                                            'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, codPedido ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codTipoDeNota not in (9) and codPedido is null ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 ' \

        dataframe = pd.read_sql(query, conn)

        nome = ano + 'Vendas'+empresa+'.csv'
        dataframe.to_csv(nome)

    elif empresa =='Varejo':
        query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, codPedido ' \
                'FROM Fat.NotaFiscal n ' \
                'where n.codPedido >= 0 ' \
                'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
                                                                   'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 and codempresa in(100, 101) '
        dataframe = pd.read_sql(query, conn)

        nome = ano + 'Vendas'+empresa+'.csv'
        dataframe.to_csv(nome)
    elif empresa == 'Outras':
        query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, codPedido ' \
                'FROM Fat.NotaFiscal n ' \
                'where n.codTipoDeNota in (48, 167, 30) ' \
                'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
                                                                   'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 and codempresa in(1, 4) '
        dataframe = pd.read_sql(query, conn)

        nome = ano + 'Vendas' + empresa + '.csv'
        dataframe.to_csv(nome)

    else:
        query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, codPedido, codNumNota, codEmpresa , codpedido ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codPedido >= 0 '   \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 and codempresa ='+ "'" + empresa + "'" \
                                                            ' union ' \
                                                            "select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado, '0' ,codNumNota, "+"'"+empresa+"', codpedido" \
            ' FROM Fat.NotaFiscal n ' \
            'where n.codTipoDeNota not in (9) and codPedido is null ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
            'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2 and codempresa ='+ "'" + empresa + "'" \

        dataframe = pd.read_sql(query, conn)
        nome = ano + 'Vendas'+empresa+'.csv'
        dataframe.to_csv(nome)



def OutrosFat(ano, empresa):
    datahora, dia = obterHoraAtual()
    tipoNota = obter_notaCsw()

    tipoNotaConsiderar = ConfTipoNota(empresa)

    conn = ConexaoCSW.Conexao()
    mesFinal, mesAtual = EncontrandoMesAtual()
    dataInicio = ano + '-' + mesAtual + '-01'
    dataFim = ano + '-12-31'
    query = 'select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado ' \
            'FROM Fat.NotaFiscal n ' \
            'where n.codTipoDeNota in (48, 167, 30) ' \
            'and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' ' \
                                                               'and n.dataEmissao <= ' + "'" + dataFim + "'" + ' and situacao = 2  and codempresa in (100, 101)'
    retornaCsw = pd.read_sql(
        "SELECT  i.codPedido, e.vlrSugestao, sum(i.qtdePecasConf) as conf , sum(i.qtdeSugerida) as qtde,  i.codSequencia,  "
        " (SELECT codTipoNota  FROM ped.Pedido p WHERE p.codEmpresa = i.codEmpresa and p.codpedido = i.codPedido) as codigo "
        " FROM ped.SugestaoPed e "
        " inner join ped.SugestaoPedItem i on i.codEmpresa = e.codEmpresa and i.codPedido = e.codPedido "
        ' WHERE e.codempresa in (100, 101)'
        " and e.dataGeracao > '2023-01-01' and situacaoSugestao = 2"
        " group by i.codPedido, e.vlrSugestao,  i.codSequencia ", conn)

    dataframe = pd.read_sql(query, conn)
    nome = ano + 'Vendas' + empresa + '.csv'
    dataframe2 = pd.read_csv(nome)

    dataframe = pd.concat([dataframe, dataframe2], ignore_index=True)

    meses = ['01-Janeiro', '02-Fevereiro', '03-Março', '04-Abril', '05-Maio', '06-Junho',
             '07-Julho', '08-Agosto', '09-Setembro', '10-Outubro', '11-Novembro', '12-Dezembro']

    faturamento_por_mes = []
    faturamento_mes_REV = []
    acumulado = 0.00
    acumuladoREV = 0.00
    faturamento_acumulado = []
    faturamento_acumulado_RV = []

    for mes in meses:
        # Filtrar os dados do mês atual
        procura = f"-{mes.split('-')[0]}-"
        dataframe48 = dataframe[dataframe['tiponota'] == 48]
        df_mes = dataframe48[dataframe48['dataEmissao'].str.contains(procura)]
        dataframeREV = dataframe[dataframe['tiponota'] == 167 | dataframe['tiponota'] == 30  ]
        df_mesREV = dataframeREV[dataframeREV['dataEmissao'].str.contains(procura)]

        # Calcular o faturamento do mês
        faturamento_mes = df_mes['faturado'].sum()
        faturamento_mesREV = df_mesREV['faturado'].sum()

        # Acumular o faturamento
        acumulado += faturamento_mes
        # Acumular o faturamento
        acumuladoREV += faturamento_mesREV

        # Formatar o faturamento do mês
        faturamento_mes = "{:,.2f}".format(faturamento_mes)
        faturamento_mes = 'R$ ' + faturamento_mes.replace(',', ';').replace('.', ',').replace(';', '.')

        # Formatar o faturamento do mês REV
        faturamento_mesREV = "{:,.2f}".format(faturamento_mesREV)
        faturamento_mesREV = 'R$ ' + faturamento_mesREV.replace(',', ';').replace('.', ',').replace(';', '.')


        if faturamento_mes == 'R$ 0,00':
            faturamento_mes = ''

        if faturamento_mesREV == 'R$ 0,00':
            faturamento_mesREV = ''

        # Formatar o acumulado
        acumulado_str = "{:,.2f}".format(acumulado)
        acumulado_str = 'R$ ' + acumulado_str.replace('.', ';')

        acumulado_str = acumulado_str.replace(',', '.')
        acumulado_str = acumulado_str.replace(';', ',')

        faturamento_por_mes.append(faturamento_mes)
        faturamento_acumulado.append(acumulado_str)

        # Formatar o acumulado
        acumulado_strRV = "{:,.2f}".format(acumuladoREV)
        acumulado_strRV = 'R$ ' + acumulado_strRV.replace('.', ';')

        acumulado_strRV = acumulado_strRV.replace(',', '.')
        acumulado_strRV = acumulado_strRV.replace(';', ',')


        faturamento_mes_REV.append(faturamento_mesREV)
        faturamento_acumulado_RV.append(acumulado_strRV)



    # Criar um DataFrame com os resultados
    df_faturamento = pd.DataFrame({'Mês': meses, 'VD Mostruario': faturamento_por_mes, 'VD Mostruario Acumulado':faturamento_acumulado,
                                   'VD Revenda MP':faturamento_mes_REV, 'VD Rv Acumulado':faturamento_acumulado_RV})
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
    df_dia = df_dia.replace(',', ".")
    df_dia = df_dia.replace(';', ",")
    df_faturamento.fillna('-', inplace=True)
    data = {
        '1- Ano:': f'{ano}',
        '2- Empresa:': f'{empresa}',
        '3- No Retorna': f"{0}",
        '3.1- Retorna Mplus': f"{0}",
        '4- No Dia': f"{df_dia}",
        '5- TOTAL': f"{total}",
        '6- Atualizado as': f"{datahora}",
        '7- Detalhamento por Mes': df_faturamento.to_dict(orient='records')
    }
    return [data]