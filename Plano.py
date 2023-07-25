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
    consulta = ConsultarPlano(codigo)
    if consulta != 0:

        query = 'Insert into pcp."Plano" (codigo, "descricao do Plano","inicioVenda","FimVenda","inicoFat","finalFat", ' \
                '"usuarioGerador","dataGeracao") values (%s, %s, %s, %s, %s, %s, %s, %s)'

        cursor = conn.cursor()
        cursor.execute(query,(codigo, descricao, iniVenda, fimVenda, iniFat, fimFat, usuario, datageracao))
        conn.commit()
        cursor.close()
        conn.close()
        return pd.DataFrame([{'Mensagem': f'Plano {codigo}-{descricao} criado com sucesso!', 'Status': True}])
    else:
        return pd.DataFrame([{'Mensagem': f'Plano {codigo} já existe!', 'Status': False}])


def ConsultarPlano(codigo):
    conn = ConexaoPostgreMPL.conexao()
    planos = pd.read_sql('SELECT * FROM pcp."Plano" '
                         ' where codigo = %s;',conn,params=(codigo))

    if not planos.empty:
        planos.rename(
            columns={'codigo': '01- Codigo Plano', 'descricao do Plano': '02- Descricao do Plano', 'inicioVenda': '03- Inicio Venda',
                     'FimVenda':'04- Final Venda',"inicoFat":"05- Inicio Faturamento","finalFat":"06- Final Faturamento",
                     'usuarioGerador':'07- Usuario Gerador','dataGeracao':'08- Data Geracao'},
            inplace=True)
        planos.fillna('-', inplace=True)

        return planos['01- Codigo Plano'][0]
    else:
        return 0