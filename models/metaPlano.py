import pandas as pd
import ConexaoPostgreMPL


def Get_Consultar(plano):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select plano, marca, "MetaR$", "Metapç" from pcp."planoMetas" '
                      'where plano = %s ',conn,params=(plano,))
    get1 = get["Metapç"].sum()
    get2 = get["MetaR$"].sum()


    get["MetaR$"] = get["MetaR$"].apply(lambda x: "{:,.0f}".format(x))
    get["Metapç"] = get["Metapç"].apply(lambda x: "{:,.0f}".format(x))

    get["MetaR$"] = get["MetaR$"].astype(str)
    get["MetaR$"] = 'R$'+get["MetaR$"].str.replace(',', '.')
    get["Metapç"] = get["Metapç"].str.replace(',', '.')

    total = pd.DataFrame([{'marca':'TOTAL',"MetaR$" :get1,"Metapç" :get2,"plano":get["plano"][0]}])

    get = pd.concat([get, total])

    return get


def InserirMeta(plano):
    conn = ConexaoPostgreMPL.conexao()



def EditarMeta(plano):
    conn = ConexaoPostgreMPL.conexao()



