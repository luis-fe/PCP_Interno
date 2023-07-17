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
    return True

def DeletarUsuarios(codigo):
    conn = ConexaoPostgreMPL.conexao()

    usuarios = pd.read_sql('delete from pcp.usuarios where codigo = %s', conn, params=(codigo,))

    if usuarios.empty:
        return pd.DataFrame['Mensagem':f'Usuario {codigo} nao encontrado !', 'Status':False]
    else:
        codigo = usuarios['codigo'][0]

        return pd.DataFrame['Mensagem':f'Usuario {codigo} excluido com sucesso !','Status':True]