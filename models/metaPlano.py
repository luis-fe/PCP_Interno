import pandas as pd
import ConexaoPostgreMPL
import numpy as np

def Get_Consultar(plano):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select plano, marca, "MetaR$", "Metapç" from pcp."planoMetas" '
                      'where plano = %s ',conn,params=(plano,))

    if not get.empty:
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
    else:
        return pd.DataFrame([{'stataus':False,'Mensagem:':'Ainda nao possue meta cadastrada'}])


def InserirMeta(plano, marca, metaReais, metaPecas ):
    conn = ConexaoPostgreMPL.conexao()
    plano = str(plano)

    pesquisa = pd.read_sql('select marca  from pcp."planoMetas" where plano = %s and marca = %s',conn,params=(plano,marca,))
    if not pesquisa.empty :
            return pd.DataFrame([{'mensagem':'Ja existe cadastro para essa marca no plano','status':False}])
    else:
        query = 'insert into pcp."planoMetas" (plano, marca, "MetaR$", "Metapç") values (%s, %s, %s ,%s )'

        cursor = conn.cursor()
        cursor.execute(query, (plano, marca, metaReais, metaPecas,))
        conn.commit()


        cursor.close()
        conn.close()

        return pd.DataFrame([{'status':True, "Mensagem":"Inclusao Realizada com sucesso"}])





def EditarMeta(plano, marcaNova, metaReaisNova = '0', metaPecasNova = '0'):
    conn = ConexaoPostgreMPL.conexao()
    plano = str(plano)
    if metaReaisNova == '0':
        metaReaisNova, x = pesquisa(plano,marcaNova)

    elif metaPecasNova == '0':
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
    try:
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
        data["1.2- PACO R$"] = data['1.2- PACO R$'].apply(lambda x: "{:,.2f}".format(x))
        data['1.2- PACO R$'] = data['1.2- PACO R$'].str.replace('.', '/')
        data['1.2- PACO R$'] = 'R$' + data['1.2- PACO R$'].str.replace(',', '.')
        data['1.2- PACO R$'] = data['1.2- PACO R$'].str.replace('/', ',')

        data['2.1- M.POLLO pçs'] = (data['2- M.POLLO %dist.']/100)*totalpçsMpollo
        data["2.1- M.POLLO pçs"] = data['2.1- M.POLLO pçs'].apply(lambda x: "{:,.0f}".format(x))
        data['2.1- M.POLLO pçs'] = data['2.1- M.POLLO pçs'].str.replace(',', '.')
        data['2.2- M.POLLO R$'] = (data['2- M.POLLO %dist.']/100)*totalreaisMpollo
        data["2.2- M.POLLO R$"] = data['2.2- M.POLLO R$'].apply(lambda x: "{:,.2f}".format(x))
        data['2.2- M.POLLO R$'] = data['2.2- M.POLLO R$'].str.replace('.', '/')
        data['2.2- M.POLLO R$'] = 'R$'+data['2.2- M.POLLO R$'].str.replace(',', '.')
        data['2.2- M.POLLO R$'] = data['2.2- M.POLLO R$'].str.replace('/', ',')






        data = {'1- Informacoes Gerais':get.to_dict(orient='records'),
                '2- Detalhamento Semanal':data.to_dict(orient='records')}

        return [data]
    except:

        return [{'Mensagem':'O Plano nao tem intervalo planejado de inicio e fim'}]



def PesquisarMetaSemana(plano, marca, semana):
    conn = ConexaoPostgreMPL.conexao()
    get = pd.read_sql('select * from pcp."PlanoMetasSemana" '
                      'where plano = %s and marca = %s and semana = %s' ,conn,params=(plano,marca, semana))
    conn.close()
    if get.empty:
        return 0
    else:

        return (get['%dist'][0]*100)

def InserindoPercentual(plano, marca, semana, Percentual_dist1 ):
    conn = ConexaoPostgreMPL.conexao()

    # Verificando se existe
    consulta = pd.read_sql('select * from pcp."PlanoMetasSemana" '
                      'where plano = %s and marca = %s and semana = %s' ,conn,params=(plano,marca, semana))

    metaTotalReais, metaTotalPecas = pesquisa(plano, marca)

    Percentual_dist = Percentual_dist1/100

    metaReais = Percentual_dist * metaTotalReais
    metaPecas = Percentual_dist * metaTotalPecas

    if not consulta.empty:



        update = 'update pcp."PlanoMetasSemana"  ' \
                 'set "_dist" = %s, "metaR$" = %s, "metaPç"= %s ' \
                 'where plano = %s and marca = %s and semana = %s'

        cursor = conn.cursor()
        cursor.execute(update, (Percentual_dist, metaReais, metaPecas, plano, marca,semana))
        conn.commit()
        cursor.close()

        retorno = pd.read_sql('select plano, marca, semana, "_dist" as distribuicao, "metaPç", "metaR$" from pcp."PlanoMetasSemana" '
                               'where plano = %s and marca = %s ', conn, params=(plano, marca))

        conn.close()
        retorno['_dist'] = retorno['_dist'] * 100
        retorno['metaPç'] = retorno['metaPç'].apply(lambda x: "{:,.0f}".format(x))
        return retorno

    else:

        insert = 'insert into "PCP".pcp."PlanoMetasSemana" (plano, marca, semana, "_dist", "metaR$", "metaPç") values (%s, %s, %s, %s, %s, %s) '

        cursor = conn.cursor()
        cursor.execute(insert, (plano, marca, semana, Percentual_dist, metaReais, metaPecas))
        conn.commit()


        retorno = pd.read_sql('select plano, marca, semana, "_dist" as distribuicao, "metaPç", "metaR$" from pcp."PlanoMetasSemana" '
                               'where plano = %s and marca = %s ', conn, params=(plano, marca))
        retorno['_dist'] = retorno['_dist']*100
        retorno['metaPç']= retorno['metaPç'].apply(lambda x: "{:,.0f}".format(x))

        cursor.close()
        return retorno







