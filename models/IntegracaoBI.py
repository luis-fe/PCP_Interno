from models import ConexaoPostgreMPL
import pandas as pd

def ConsultarLotesPlanos():
    conn = ConexaoPostgreMPL.conexao()
    consulta = pd.read_sql('select distinct lote, plano from pcp."LoteporPlano"',conn)
    return consulta
