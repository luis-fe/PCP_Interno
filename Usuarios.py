import ConexaoPostgreMPL
import pandas as pd


def ObterUsuarios():
    conn = ConexaoPostgreMPL.conexao()

    usuarios = pd.read_sql('select * from pcp.usuarios',conn)

    return usuarios

def ObterUsuariosCodigo(codigo):
    conn = ConexaoPostgreMPL.conexao()

    usuarios = pd.read_sql('select * from pcp.usuarios where codigo = %s', conn, params=(codigo,))

    if usuarios.empty:
        CodigoAtual = 0
    else:
        CodigoAtual = usuarios['codigo'][0]

    return CodigoAtual

def InserirUsuario(codigo, nome, senha):
    conn = ConexaoPostgreMPL.conexao()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO "pcp"."usuarios" (codigo, nome, senha) '
                   'VALUES (%s, %s, %s)',(codigo, nome, senha))
    conn.commit()
    cursor.close()
    conn.close()
    return pd.DataFrame['Status':True, 'Mensagem':f'Usuario{nome} cadastrado com sucesso']