import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL
from datetime import datetime


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
                 'where codigo = %s '
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

def DeletarPlano(codigo):
    conn = ConexaoPostgreMPL.conexao()

    cursor = conn.cursor()
    cursor.execute('DELETE FROM pcp."Plano" WHERE codigo = %s', (codigo,))
    conn.commit()
    deleted_rows = cursor.rowcount

    if deleted_rows == 0:
        return pd.DataFrame([{'Mensagem': f'UsuÃ¡rio {codigo} não encontrado!', 'Status': False}])
    else:
        return pd.DataFrame([{'Mensagem': f'UsuÃ¡rio {codigo} excluído com sucesso!', 'Status': True}])

def ObeterColecoesPlano(plano):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('SELECT plano, colecao, nomecolecao FROM pcp."colecoesPlano" '
                         ' where plano = %s',conn,params=(plano,))
    planos.rename(
        columns={'plano': '01- Codigo Plano', 'colecao': '02- colecao', 'nomecolecao': '03- nomecolecao'},
        inplace=True)

    planos.fillna('-', inplace=True)

    return planos
def ObeterNotasPlano(plano):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('select distinct plano, "tipo nota", "nome" from pcp."tipoNotaporPlano" '
                         ' where plano = %s',conn,params=(plano,))
    planos.rename(
        columns={'plano': '01- Codigo Plano', 'tipo nota': '02- tipo nota', 'nome': '03- nomeTipoNota'},
        inplace=True)

    planos.fillna('-', inplace=True)

    return planos
def ObeterLotesPlano(plano):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('select plano, nomelote, lote from pcp."LoteporPlano" '
                         ' where plano = %s',conn,params=(plano,))
    planos.rename(
        columns={'plano': '01- Codigo Plano', 'lote': '02- lote', 'nomelote': '03- nomelote'},
        inplace=True)

    planos.fillna('-', inplace=True)

    return planos

def InserirColecaoNoPlano(plano, colecao, nomecolecao):
    conn = ConexaoPostgreMPL.conexao()
   # colecao = colecao.split(", ")
   # nomecolecao = nomecolecao.split(", ")

    c = 0
    for i in range(len(colecao)):
        x = ConsularColecaoPlano(plano, colecao[i])
        y = ConsultarPlano(plano)
        if x == True and y !=0 :
            qurery = 'insert into pcp."colecoesPlano" (plano, colecao, nomecolecao) values (%s, %s , %s)'
            cursor = conn.cursor()
            cursor.execute(qurery, (plano, colecao[i], nomecolecao[i]))
            conn.commit()
            cursor.close()
            c = i

        else:
            c = 0
    conn.close()
    return c
def InserirNotaNoPlano(plano, nota, nome):
    conn = ConexaoPostgreMPL.conexao()
   # colecao = colecao.split(", ")
   # nomecolecao = nomecolecao.split(", ")

    c = 0
    for i in range(len(nota)):
        x = ConsularColecaoPlano(plano, nota[i])
        y = ConsultarPlano(plano)
        if x == True and y !=0 :
            qurery = 'insert into pcp."tipoNotaporPlano" (plano, "tipo nota", nome) values (%s, %s , %s)'
            cursor = conn.cursor()
            cursor.execute(qurery, (plano, nota[i], nome[i]))
            conn.commit()
            cursor.close()
            c = i

        else:
            c = 0
    conn.close()
    return c

def InserirLoteNoPlano(plano, lote, nome):
    conn = ConexaoPostgreMPL.conexao()
   # colecao = colecao.split(", ")
   # nomecolecao = nomecolecao.split(", ")

    c = 0
    for i in range(len(lote)):
        x = ConsularColecaoPlano(plano, lote[i])
        y = ConsultarPlano(plano)
        if x == True and y !=0 :
            qurery = 'insert into pcp."LoteporPlano" (plano, "lote", nomelote) values (%s, %s , %s)'
            cursor = conn.cursor()
            cursor.execute(qurery, (plano, lote[i], nome[i]))
            conn.commit()
            cursor.close()
            c = i

        else:
            c = 0
    conn.close()
    return c



def ConsularColecaoPlano(plano, colecao):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('SELECT plano, colecao, nomecolecao FROM pcp."colecoesPlano" '
                         ' where plano = %s and colecao = %s',conn,params=(plano,colecao,))

    if  planos.empty:
        return True
    else:
        return False
def ConsularLote(plano, lote):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('SELECT plano, lote, nomelote FROM pcp."LoteporPlano" '
                         ' where plano = %s and colecao = %s',conn,params=(plano,lote,))

    if  planos.empty:
        return True
    else:
        return False
def ConsularNota(plano, nota):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('SELECT plano, "tipo nota", nome FROM pcp."tipoNotaporPlano" '
                         ' where plano = %s and "tipo nota" = %s',conn,params=(plano,nota,))

    if  planos.empty:
        return True
    else:
        return False

def DeletarPlanoColecao(codigo, codcolecao):
    conn = ConexaoPostgreMPL.conexao()
    c = 0
    for i in range(len(codcolecao)):

        cursor = conn.cursor()
        cursor.execute('DELETE FROM pcp."colecoesPlano" WHERE plano = %s and colecao = %s', (codigo,codcolecao[i]))
        conn.commit()
        c = 1

    if c == 0:
        return pd.DataFrame([{'Mensagem': f'colecao {codcolecao} não encontrada no plano {codigo}', 'Status': False}])
    else:
        return pd.DataFrame([{'Mensagem': f'colecao {codcolecao} excluído com sucesso do plano {codigo}!', 'Status': True}])

def DeletarPlanoLote(codigo, codLote):
    conn = ConexaoPostgreMPL.conexao()
    c = 0
    for i in range(len(codLote)):

        cursor = conn.cursor()
        cursor.execute('DELETE FROM pcp."LoteporPlano" WHERE plano = %s and lote = %s', (codigo,codLote[i]))
        conn.commit()
        c = 1

    if c == 0:
        return pd.DataFrame([{'Mensagem': f'lote {codLote} não encontrada no plano {codigo}', 'Status': False}])
    else:
        return pd.DataFrame([{'Mensagem': f'lote {codLote} excluído com sucesso do plano {codigo}!', 'Status': True}])

def DeletarPlanoNota(codigo, tipoNota):
    conn = ConexaoPostgreMPL.conexao()
    c = 0
    for i in range(len(tipoNota)):

        cursor = conn.cursor()
        cursor.execute('DELETE FROM pcp."tipoNotaporPlano" WHERE plano = %s and "tipo nota" = %s', (codigo,tipoNota[i]))
        conn.commit()
        c = 1

    if c == 0:
        return pd.DataFrame([{'Mensagem': f'tipo nota {tipoNota} não encontrada no plano {codigo}', 'Status': False}])
    else:
        return pd.DataFrame([{'Mensagem': f'tipo nota {tipoNota} excluído com sucesso do plano {codigo}!', 'Status': True}])

def DuracaoPlano(plano):
    conn = ConexaoPostgreMPL.conexao()
    semanas = pd.read_sql('select "inicioVenda", "FimVenda" from pcp."Plano" where "Plano" = s% ',conn,params=(plano,))

    iniVenda = semanas['inicioVenda'][0]
    FimVenda = semanas['FimVenda'][0]
    # Converter as strings em objetos de data
    iniVenda = datetime.strptime(iniVenda, '%Y-%m-%d')
    FimVenda = datetime.strptime(FimVenda, '%Y-%m-%d')

    # Calcular a diferença em dias entre as datas
    dias = (FimVenda - iniVenda).days
    semanas = dias /7

    return print(semanas)



