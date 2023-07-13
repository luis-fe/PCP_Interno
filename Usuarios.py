import ConexaoPostgreMPL
import pandas as pd


def ObterUsuarios():
    conn = ConexaoPostgreMPL.conexao()

    usuarios = pd.read_sql('select * from pcp.usuarios',conn)

    return usuarios