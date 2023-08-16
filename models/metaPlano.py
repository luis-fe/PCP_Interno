import pandas as pd
import ConexaoPostgreMPL
import numpy as np

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
    get['Duracao'] = get['FimVenda'] [0] - get['inicioVenda'] [0]
    get['Duracao'] = get['Duracao'].astype(str)
    get['Total semanas'] = get['Duracao'].str.extract('(\d+)').astype(int)
    get['Total semanas'] = get['Total semanas']/7
    get['Total semanas'] = np.ceil(get['Total semanas'])
    get['Total semanas'] = get['Total semanas'] .astype(int)
    get.drop(['inicioVenda','FimVenda'], axis=1, inplace=True)


    conn.close()
    data = pd.DataFrame([{'0-semana':1}])
    for i in range(get['Total semanas'][0]-2):
        novo = {'0-semana':(i+2)}
        data = data.append(novo,ignore_index=True )
    data['0-semana'] = data['0-semana'].astype(str)
    data['1- PACO %dist.'] = data.apply(lambda row: PesquisarMetaSemana(plano, 'PACO', row['0-semana']), axis=1)
    data['2- M.POLLO %dist.'] = data.apply(lambda row: PesquisarMetaSemana(plano, 'MPOLLO', row['0-semana']), axis=1)
    totalreais , totalpçs = pesquisa(plano,'PACO')
    totalreaisMpollo, totalpçsMpollo = pesquisa(plano, 'M.POLLO')

    data['1.1- PACO pçs'] = (data['1- PACO %dist.']/100)*totalpçs
    data["1.1- PACO pçs"] = data["1.1- PACO pçs"].apply(lambda x: "{:,.0f}".format(x))

    data['1.2- PACO R$'] = (data['1- PACO %dist.']/100)*totalreais
    data['1.1- PACO pçs'] = data['1.1- PACO pçs'] .astype(int)
    data['2.1- M.POLLO pçs'] = (data['2- M.POLLO %dist.']/100)*totalpçsMpollo
    data['2.2- M.POLLO R$'] = (data['2- M.POLLO %dist.']/100)*totalreaisMpollo
    data['2.1- M.POLLO pçs'] = data['2.1- M.POLLO pçs'] .astype(int)





    data = {'1- Informacoes Gerais':get.to_dict(orient='records'),
            '2- Detalhamento Semanal':data.to_dict(orient='records')}

    return [data]



def PesquisarMetaSemana(plano, marca, semana):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select * from pcp."PlanoMetasSemana" '
                      'where plano = %s and marca = %s and semana = %s' ,conn,params=(plano,marca, semana))
    conn.close()
    if get.empty:
        return 0
    else:

        return (get['%dist'][0]*100)