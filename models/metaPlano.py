import pandas as pd
import ConexaoPostgreMPL


def Get_Consultar(plano):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select plano, marca, "MetaR$", "Metapç" from pcp."planoMetas" '
                      'where plano = %s ',conn,params=(plano,))
    get1 = get["MetaR$"].sum()
    get2 = get["Metapç"].sum()
    get1 = "{:,.0f}".format(get1)
    get2 = "{:,.0f}".format(get2)
    get1 = 'R$'+str(get1)
    get2 = str(get2)
    get1 = get1.replace(',', '.')
    get2 = get2.replace(',', '.')


    get["MetaR$"] = get["MetaR$"].apply(lambda x: "{:,.0f}".format(x))
    get["Metapç"] = get["Metapç"].apply(lambda x: "{:,.0f}".format(x))

    get["MetaR$"] = get["MetaR$"].astype(str)
    get["MetaR$"] = 'R$'+get["MetaR$"].str.replace(',', '.')
    get["Metapç"] = get["Metapç"].str.replace(',', '.')

    total = pd.DataFrame([{'marca':'TOTAL',"MetaR$" :get1,"Metapç" :get2,"plano":get["plano"][0]}])

    get = pd.concat([get, total])

    return get


def InserirMeta(plano, marca, metaReais, metaPecas ):
    conn = ConexaoPostgreMPL.conexao()
    query = 'insert into pcp."planoMetas" (plano, marca, "MetaR$", "Metapç") values (%s, %s, %s ,%s )'
    cursor = conn.cursor()
    cursor.execute(query, (plano, marca, metaReais, metaPecas,))
    conn.commit()


    cursor.close()
    conn.close()

    return pd.DataFrame([{'status':True, "Mensagem":"Inclusao Realizada com sucesso"}])





def EditarMeta(plano, marcaNova, metaReaisNova = '0', metaPecasNova = '0'):
    conn = ConexaoPostgreMPL.conexao()
    if metaReaisNova == 0:
        metaReaisNova, x = pesquisa(plano,marcaNova)

    elif metaPecasNova == 0:
        x, metaPecasNova = pesquisa(plano,marcaNova)

    else:
        print('segue o baile')

    update = 'update pcp."planoMetas" set marca = %s, "MetaR$" = %s, "Metapç" = %s ' \
             'where plano = %s and marca = %s '
    cursor = conn.cursor()
    cursor.execute(update, ( marcaNova, metaReaisNova, metaPecasNova, plano, marcaNova,))
    conn.commit()


    cursor.close()
    conn.close()

    return pd.DataFrame([{'status':True, "Mensagem":"Alteracao Realizada com sucesso"}])



def pesquisa(plano, marca):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select plano, marca, "MetaR$", "Metapç" from pcp."planoMetas" '
                      'where plano = %s and marca = %s',conn,params=(plano,marca))
    conn.close()

    return get['MetaR$'][0], get['Metapç'][0]

def metasSemanais(plano):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select "inicioVenda", "FimVenda" from pcp."Plano" where codigo = %s',conn,params=(plano,))
    get['inicioVenda'] = pd.to_datetime(get['inicioVenda'], format='%d/%m/%Y')
    get['FimVenda'] = pd.to_datetime(get['FimVenda'], format='%d/%m/%Y')
    get['intervalo'] = get['FimVenda'] [0] - get['inicioVenda'] [0]
    get['intervalo'] = get['intervalo'].astype(int)
    conn.close()

    return get



