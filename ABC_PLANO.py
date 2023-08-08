import pandas as pd
import ConexaoPostgreMPL

def Editar(a, b, c, c1, c2, c3, plano):
    a1, b1, c1 = ABC_Plano(plano)
    a2 = Atualizacao(a1, a)
    b2 = Atualizacao(a1, b)
    c2 = Atualizacao(a1, c)

    update = 'update pcp."ABC_Plano" ' \
             'set a = %s , b = %s , c = %s ' \
             'WHERE plano = %s '
    conn = ConexaoPostgreMPL.conexao()

    cursor = conn.cursor()

    cursor.excute(update,(a2, b2, c2, plano,))

    cursor.commit()
    cursor.close()
    conn.close()

    return pd.DataFrame([{'status':True,'Mensagem':'Salvo com sucesso !'}])






def ABC_Plano(plano):
    conn = ConexaoPostgreMPL.conexao()
    query = pd.read_sql('Select  a, b, c from pcp."ABC_Plano" WHERE plano = %s ',conn,params=(plano,))

    return query['a'][0],query['b'][0],query['c'][0]

def Atualizacao(antigo, novo):
    if novo == '0':
        return  antigo
    else:
        return novo
