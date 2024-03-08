import pandas as pd

import BuscasAvancadas
import ConexaoCSW


def AnaliseVendasOutlet():
    conn = ConexaoCSW.Conexao()

    CapaPedidos = pd.read_sql(BuscasAvancadas.CapaPedido(1,'2024-01-01','2024-09-01','145'),conn)
    #CapaPedidos = pd.read_sql(BuscasAvancadas.TipoOP(), conn)
   # PedidosSkus = pd.read_sql(BuscasAvancadas.pedidosNivelSKU(1,'2024-01-01','2024-09-01','145'),conn)

    #analise = pd.merge(CapaPedidos,PedidosSkus,on='codPedido',how='left')

    conn.close()

    return CapaPedidos

