import pandas as pd
import ConexaoPostgreMPL
import ConexaoCSW

##Arquivo utilizado para cadastrar aS justificativas de LeadTime das OPS que estouraram o LEADTIME.

def CadastrarJustificativa(ordemProd, fase , justificativa):
    consultar = ConsultarJustificativa(ordemProd, fase)

    if consultar['justificativa'] == 'sem justificativa':
        conn = ConexaoPostgreMPL.conexao()

        insert = 'INSERT INTO "PCP".pcp.justificativa (ordemprod, fase, justificativa) values ' \
                 '(%s , %s, %s )'

        cursor = conn.cursor()
        cursor.execute (insert,(ordemProd, fase, justificativa))
        conn.commit()
        cursor.close()

        conn.close()
        return pd.DataFrame([{'mensagem':'Dados Inseridos com sucesso !'}])

    else:

        return pd.DataFrame([{'mensagem':'Dados Inseridos com sucesso !!'}])



def ConsultarJustificativa(ordemProd, fase):
    conn = ConexaoPostgreMPL.conexao()
    conn2 = ConexaoCSW.Conexao()

    consulta1 = 'SELECT ordemprod as "numeroOP", fase as "codFase", justificativa FROM "PCP".pcp.justificativa ' \
                'WHERE ordemprod = %s and fase = %s '

    consulta1 = pd.read_sql(consulta1,conn,params=(ordemProd, fase,))


    consulta2 =pd.read_sql('SELECT CONVERT(varchar(12), codop) as numeroOP, codfase as codFase, textolinha as justificativa FROM tco.ObservacoesGiroFasesTexto  t '
                                    'WHERE empresa = 1 and textolinha is not null',conn2)
    consulta2['codFase'] = consulta2['codFase'].astype(str)

    consulta2 = consulta2[consulta2['numeroOP'] == ordemProd]
    consulta2 = consulta2[consulta2['codFase'] == str(fase)]


    if consulta2.empty and not consulta1.empty:
        consulta = consulta1

    elif consulta2.empty and consulta1.empty:
        consulta = pd.DataFrame([{'justificativa': 'sem justificativa'}])

    else:
        consulta = pd.concat([consulta1 , consulta2])

    conn.close()
    conn2.close()

    return consulta
