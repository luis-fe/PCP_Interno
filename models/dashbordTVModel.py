import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL


def Faturamento_ano(ano, empresa):
    dataInicio = ano + '-01-01'
    dataFim = ano + '-12-31'
    conn = ConexaoCSW.Conexao()
    dataframe = pd.read_sql('select n.codTipoDeNota as tiponota, n.dataEmissao, n.vlrTotal as faturado'
                            '  FROM Fat.NotaFiscal n '
                            'where n.codEmpresa = ' + empresa + ' and n.codPedido >= 0 and n.dataEmissao >= ' + "'" + dataInicio + "'" + ' '
                            'and n.dataEmissao <= ' + "'" + dataFim + "'" + 'and situacao = 2 ',conn)
    # Filtrando os dados de janeiro
    Janeiro = dataframe[dataframe['dataEmissao'].str.contains('-01-')]

    # Calculando a soma dos valores faturados em janeiro
    Janeiro_faturado = Janeiro['faturado'].sum()

    # Criando um DataFrame com o resultado
    df_janeiro = pd.DataFrame({'Mês': ['Janeiro'], 'Faturado': [Janeiro_faturado]})

    return df_janeiro