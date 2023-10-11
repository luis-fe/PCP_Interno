import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL

def Faturamento_ano(ano, empresa):
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

    # Criar um DataFrame com os resultados
    df_faturamento = pd.DataFrame({'Mês': meses, 'Faturado': faturamento_por_mes})

    data = {
        '1- Ano:': f'{ano}',
        '2- Empresa:': f'{empresa}',
        '3- No Retorna':"",
        '4- No Dia': "",
        '5- Detalhamento por Mes': df_faturamento.to_dict(orient='records')
    }
    return [data]


