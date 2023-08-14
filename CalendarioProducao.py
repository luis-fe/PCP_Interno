import pandas as pd
import datetime

import ConexaoPostgreMPL


def InserirPadrao_FeriadosPlano(plano):
    feriados = PlanilhaFeriados(plano)
    if feriados.empty:
        return False
    else:

        conn = ConexaoPostgreMPL.conexao()
        query = 'insert into pcp."CadastroFeriados" (data, "descricaoFeriado","plano") VALUES (%s, %s, %s)'
        cursor = conn.cursor()

        for i in range(feriados['data'].size):
            datai = feriados['data'][i].date()  # Convertendo Timestamp para date
            descricao = feriados['descricao'][i]
            cursor.execute(query,(datai,descricao,plano))
            conn.commit()

        cursor.close()
        conn.close()
        return True




def PlanilhaFeriados(plano):
    data_inicial , data_final = PesquisaPlano(plano)
    if data_inicial == False:
        return pd.DataFrame([{}])
    else:
        feriados = pd.read_csv('Feriados.csv',delimiter=';')
        feriados['data']  = pd.to_datetime(feriados['data'])
        feriados = feriados[(feriados['data'] >= data_inicial) & (feriados['data'] <= data_final)]
        feriados = feriados.reset_index(drop=True)
        return feriados



def PesquisaPlano (plano):
    conn = ConexaoPostgreMPL.conexao()
    plano_df = pd.read_sql('select "inicioVenda", "finalFat" from pcp."Plano" '
                        'where codigo = %s', conn,params=(plano,))
    conn.close()
    plano_df.fillna('-', inplace=True)
    plano_df['inicioVenda'] = pd.to_datetime(plano_df['inicioVenda'], format='%d/%m/%Y')
    plano_df['finalFat'] = pd.to_datetime(plano_df['finalFat'], format='%d/%m/%Y')


    if plano_df['inicioVenda'][0] =='-' or plano_df['finalFat'][0] =='-':
        return False, False
    else:

        # Converter as colunas para o formato de data
        data_inicial = plano_df['inicioVenda'][0]
        finalFat = plano_df['finalFat'][0]
        print(plano_df.dtypes)


        return data_inicial, finalFat

def Avaliar_ExisteFeriadoPadrao(plano):
    conn = ConexaoPostgreMPL.conexao()
    plano_df = pd.read_sql('select * from pcp."CadastroFeriados" '
                           'where plano = %s', conn, params=(plano,))
    conn.close()

    if plano_df.empty:
        return True
    else:
        return False

def Get_feriados(plano):
    conn = ConexaoPostgreMPL.conexao()
    plano_df = pd.read_sql('select * from pcp."CadastroFeriados" '
                           'where plano = %s', conn, params=(plano,))
    conn.close()

    return plano_df

