import pandas as pd
import ConexaoCSW
import ConexaoPostgreMPL

def ObeterPlanos():
    conn = ConexaoPostgreMPL
    planos = pd.read_sql('SELECT * FROM pcp."Plano" '
                         ' ORDER BY codigo ASC;',conn)
    return planos