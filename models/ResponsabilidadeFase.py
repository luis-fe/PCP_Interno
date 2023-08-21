import pandas as pd
import ConexaoPostgreMPL
from datetime import datetime

from models import ObterInfCSW


def Inserir(codFase, responsavel):
    conn = ConexaoPostgreMPL.conexao()

    codfase2, nome2 = Pesquisa(codFase)

    if codfase2 == 'novo':
        insert = 'insert into pcp."responsabilidadeFase"("codFase","responsavel") ' \
                 'values (%s , %s)'
        cursor = conn.cursor()
        cursor.execute (insert,(codFase,responsavel))
        conn.commit()
        cursor.close()
        conn.close()
        return pd.DataFrame([{'status':True,"Mensagem":'responsavel atribuido com sucesso'}])
    else:
        return pd.DataFrame([{'status': False, "Mensagem": 'Fase ja existe responsavel atribuido'}])


def Pesquisa(codFase):
    conn = ConexaoPostgreMPL.conexao()
    procurar = pd.read_sql('select * from pcp."responsabilidadeFase" where "codFase" = %s',conn,params=(codFase,))

    if procurar.empty:
        return 'novo', 'novo'
    else:
        return procurar['codFase'][0], procurar['responsavel'][0]
def ObterFaseResponsais(nomefase = '0', responsavel = '0', codFase = '0'):
    conn = ConexaoPostgreMPL.conexao()
    fasecsw = ObterInfCSW.GetTipoFases()
    faseRespo = pd.read_sql('select * from pcp."responsabilidadeFase"',conn)
    fasecsw = pd.merge(fasecsw,faseRespo,on='codFase',how='left')
    fasecsw.fillna('-', inplace=True)

    fasecsw = TemFiltro(nomefase.upper(), fasecsw, 'nomefase')
    fasecsw = TemFiltro(responsavel.upper(), fasecsw, 'responsavel')
    fasecsw = TemFiltro(codFase, fasecsw, 'codFase')

    return fasecsw

def AlterarResponsalvel(codFase,responsavel):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    tamanho_Lista = len(codFase)
    for i in range(tamanho_Lista):
        codFase2 = codFase[i]
        nome2 = responsavel[i]
        update = 'update pcp."responsabilidadeFase" ' \
                 ' set "responsavel" = %s ' \
                 'where "codFase" = %s '
        cursor = conn.cursor()
        cursor.execute (update,(nome2,codFase2,))
        conn.commit()

    cursor.close()
    conn.close()
    return pd.DataFrame([{'status':True,"Mensagem":f'responsaveis alterado com sucesso : {tamanho_Lista} alteracoes'}])


def TemFiltro(nomedofiltro,dataframe, coluna):
    if nomedofiltro == '0':
        estrutura = dataframe
        return estrutura
    else:
        dataframe = dataframe[dataframe[coluna].str.contains(nomedofiltro)]
        dataframe = dataframe.reset_index(drop=True)
        print(coluna)
        return dataframe
