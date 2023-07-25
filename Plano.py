import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL

def ObeterPlanos():
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('SELECT * FROM pcp."Plano" '
                         ' ORDER BY codigo ASC;',conn)
    planos.rename(
        columns={'codigo': '01- Codigo Plano', 'descricao do Plano': '02- Descricao do Plano', 'inicioVenda': '03- Inicio Venda',
                 'FimVenda':'04- Final Venda',"inicoFat":"05- Inicio Faturamento","finalFat":"06- Final Faturamento",
                 'usuarioGerador':'07- Usuario Gerador','dataGeracao':'08- Data Geracao'},
        inplace=True)
    planos.fillna('-', inplace=True)

    return planos

def InserirPlano(codigo, descricao, iniVenda, fimVenda, iniFat, fimFat, usuario, datageracao):
    conn = ConexaoPostgreMPL.conexao()

    query = 'Insert into pcp."Plano" (codigo, "descricao do Plano","inicioVenda","FimVenda","inicoFat","finalFat", ' \
                '"usuarioGerador","dataGeracao") values (%s, %s, %s, %s, %s, %s, %s, %s)'

    cursor = conn.cursor()
    cursor.execute(query,(codigo, descricao, iniVenda, fimVenda, iniFat, fimFat, usuario, datageracao))
    conn.commit()
    cursor.close()
    conn.close()
    return pd.DataFrame([{'Mensagem': f'Plano {codigo}-{descricao} criado com sucesso!', 'Status': True}])



def ConsultarPlano(codigo):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('SELECT * FROM pcp."Plano" '
                         ' where codigo = %s ;',conn,params=(codigo,))

    if not planos.empty:
        planos.rename(
            columns={'codigo': '01- Codigo Plano', 'descricao do Plano': '02- Descricao do Plano', 'inicioVenda': '03- Inicio Venda',
                     'FimVenda':'04- Final Venda',"inicoFat":"05- Inicio Faturamento","finalFat":"06- Final Faturamento",
                     'usuarioGerador':'07- Usuario Gerador','dataGeracao':'08- Data Geracao'},
            inplace=True)
        planos.fillna('-', inplace=True)

        return planos['01- Codigo Plano'][0], planos['02- Descricao do Plano'][0],planos['03- Inicio Venda'][0],planos['04- Final Venda'][0],\
            planos['05- Inicio Faturamento'][0],planos['06- Final Faturamento'][0]
    else:
        return 0, 0,0,0,0,0


def EditarPlano(codigo, descricaoNova='0',iniVendaNova = '0', finalVendaNova = '0', inicoFatNovo = '0', finalFatNovo ='0'):
    codigo2, descricaoAnt, iniVendaAnt, finalVendaAnt, inicioFatAnt, finalFatAnt = ConsultarPlano(codigo)
    if codigo2 != 0:
        descricaoNova = Conversao(descricaoNova,descricaoAnt)
        iniVendaNova = Conversao(iniVendaNova,iniVendaAnt)
        finalVendaNova = Conversao(finalVendaNova, finalVendaAnt)
        inicoFatNovo = Conversao(inicoFatNovo, inicioFatAnt)
        finalFatNovo = Conversao(finalFatNovo, finalFatAnt)



        conn = ConexaoPostgreMPL.conexao()
        update = 'update pcp."Plano"' \
                 ' set "descricao do Plano" = %s , "inicioVenda" = %s , "FimVenda"= %s, "inicoFat" = %s , "finalFat" = %s ' \
                 'where codigo = %s'
        cursor = conn.cursor()
        cursor.execute(update,(descricaoNova,iniVendaNova,finalVendaNova,inicoFatNovo, finalFatNovo,codigo))
        conn.commit()


        return codigo2, descricaoNova, iniVendaNova, finalVendaNova, inicoFatNovo, finalFatNovo
    else:
        return False, False , False, False, False

def Conversao(valornovo, valorAntigo):
    if valornovo == '0':
        valornovo = valorAntigo
        return valornovo
    else:
        return valornovo

