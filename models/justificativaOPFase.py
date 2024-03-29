import pandas as pd
import ConexaoPostgreMPL
import ConexaoCSW

##Arquivo utilizado para cadastrar aS justificativas de LeadTime das OPS que estouraram o LEADTIME.

def CadastrarJustificativa(ordemProd, fase , justificativa):
    fase = str(fase)
    consultar = ConsultarJustificativa(ordemProd, fase)

    if consultar['justificativa'][0] == 'sem justificativa':
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
        conn = ConexaoPostgreMPL.conexao()

        update = 'update "PCP".pcp.justificativa set justificativa = %s where ' \
                 ' ordemprod = %s and fase = %s '

        cursor = conn.cursor()
        cursor.execute (update,( justificativa, ordemProd, fase))
        conn.commit()
        cursor.close()

        conn.close()

        return pd.DataFrame([{'mensagem':'Dados Inseridos com sucesso !!'}])



def ConsultarJustificativa(ordemProd, fase):
    conn = ConexaoPostgreMPL.conexao()
    conn2 = ConexaoCSW.Conexao()

    consultaPostgre = 'SELECT ordemprod as "numeroOP", fase as "codFase", justificativa FROM "PCP".pcp.justificativa ' \
                'WHERE ordemprod = %s and fase = %s '

    consultaPostgre = pd.read_sql(consultaPostgre,conn,params=(ordemProd, fase,))


    consulta2 =pd.read_sql('SELECT CONVERT(varchar(12), codop) as numeroOP, codfase as codFase, textolinha as justificativa FROM tco.ObservacoesGiroFasesTexto  t '
                                    'WHERE empresa = 1 and textolinha is not null',conn2)
    consulta2['codFase'] = consulta2['codFase'].astype(str)

    consulta2 = consulta2[consulta2['numeroOP'] == ordemProd]
    consulta2 = consulta2[consulta2['codFase'] == str(fase)]

    conn.close()
    conn2.close()

    if consulta2.empty and not consultaPostgre.empty:
        consulta = consultaPostgre
        print('teste1')

    elif consulta2.empty and consultaPostgre.empty:
        consulta = pd.DataFrame([{'justificativa': 'sem justificativa'}])

    elif not consulta2.empty and consultaPostgre.empty:

        consulta = pd.DataFrame([{'justificativa': 'sem justificativa'}])


    else:
        consulta = consultaPostgre


    return consulta
