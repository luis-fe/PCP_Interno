import pandas as pd
import ConexaoPostgreMPL


def Get_Consultar(plano):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select plano, marca, "MetaR$", "Metapç" from pcp."planoMetas" '
                      'where plano = %s ',conn,params=(plano,))

    get["MetaR$"] = get["MetaR$"].apply(lambda x: "{:,.0f}".format(x))
    get["MetaR$"]= get["MetaR$"].astype(str)
    get["MetaR$"] = get["MetaR$"].str.replace(',', '.')


    return get


def InserirMeta(plano):
    conn = ConexaoPostgreMPL.conexao()


def EditarMeta(plano):
    conn = ConexaoPostgreMPL.conexao()



