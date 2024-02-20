import pandas as pd
import ConexaoPostgreMPL
import ConexaoCSW

##Arquivo utilizado para cadastrar aS justificativas de LeadTime das OPS que estouraram o LEADTIME.

def CadastrarJustificativa(ordemProd, fase , justificativa):
    conn = ConexaoPostgreMPL.conexao()

    insert = 'INSERT INTO "PCP".pcp.justificativa (ordemprod, fase, justificativa) values ' \
             '(%s , %s, %s )'

    cursor = conn.cursor()
    cursor.execute (insert,(ordemProd, fase, justificativa))
    conn.commit()
    cursor.close()

    conn.close()
    return pd.DataFrame([{'mensagem':'Dados Inseridos com sucesso !'}])


def ConsultarJustificativa(ordemProd, fase):
    conn = ConexaoPostgreMPL.conexao()
    conn2 = ConexaoCSW.Conexao()

    consulta1 = 'SELECT * FROM "PCP".pcp.justificativa ' \
                'WHERE ordemprod = %s and fase = %s '

    consulta1 = pd.read_sql(consulta1,conn,params=(ordemProd, fase,))

    ordemProd = "'%"+ordemProd+"%'"
    fase = "'%"+fase+"%'"

    consulta2 = 'SELECT CONVERT(varchar(12), codop) as ordemprod, codfase as fase, textolinha as justificativa FROM tco.ObservacoesGiroFasesTexto  t ' \
                ' having ordemprod like '+ordemProd+ ' and '+fase
    consulta2 = pd.read_sql(consulta2,conn2)

    if consulta2.empty and not consulta2.empty:
        consulta = consulta1

    elif consulta2.empty and consulta2.empty:
        consulta = pd.DataFrame([{'justificativa': '-'}])

    else:
        consulta = pd.concat({consulta1 , consulta2})

    conn.close()
    conn2.close()

    return consulta
