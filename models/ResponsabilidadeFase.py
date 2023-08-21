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
def ObterFaseResponsais():
    conn = ConexaoPostgreMPL.conexao()
    fasecsw = ObterInfCSW.GetTipoFases()
    faseRespo = pd.read_sql('select * from pcp."responsabilidadeFase"',conn)
    fasecsw = pd.merge(fasecsw,faseRespo,on='codFase',how='left')
    fasecsw.fillna('-', inplace=True)

    return fasecsw

def AlterarResponsalvel(codFase,responsavel):
    conn = ConexaoPostgreMPL.conexao()

    tamanho_Lista = len(codFase)
    '''''
    codfase2, nome2 = Pesquisa(codFase)

    if codfase2 != 'novo':
        update = 'update pcp."responsabilidadeFase" ' \
                 ' set "responsavel" = %s ' \
                 'where "codFase" = %s '
        cursor = conn.cursor()
        cursor.execute (update,(responsavel,codFase,))
        conn.commit()
        cursor.close()
        conn.close()
  '''''
    return pd.DataFrame([{'status':True,"Mensagem":f'responsavel alterado com sucesso {tamanho_Lista}'}])

#    else:
 #       return pd.DataFrame([{'status': False, "Mensagem": 'Fase nao existe'}])


