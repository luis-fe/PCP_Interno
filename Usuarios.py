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

    cursor = conn.cursor()
    cursor.execute('DELETE FROM pcp.usuarios WHERE codigo = %s', (codigo,))
    conn.commit()
    deleted_rows = cursor.rowcount

    if deleted_rows == 0:
        return pd.DataFrame({'Mensagem': f'Usuário {codigo} não encontrado!', 'Status': False})
    else:
        return pd.DataFrame({'Mensagem': f'Usuário {codigo} excluído com sucesso!', 'Status': True})
