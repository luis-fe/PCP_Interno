import pandas as pd
import BuscasAvancadas
import ConexaoCSW
import ConexaoPostgreMPL


#Carregando a Capa de pedidos do CSW : BuscasAvancadas.CapaPedido (empresa, iniVenda, finalVenda, tiponota):
def Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota):
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.CapaPedido(empresa, iniVenda, finalVenda, tiponota), conn)

    conn.close()
    return consulta


# Verfiicando se o pedido nao está bloqueado :
def Monitor_PedidosBloqueados():
    conn = ConexaoCSW.Conexao()
    consulta = pd.read_sql(BuscasAvancadas.SituacaoPedidos(), conn)

    conn.close()
    return consulta


#Carregando os Pedidos a nivel Sku


def MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota):
    #Convertendo tipo de nota em string "1,2, 3, .."

    tiponota2 = ""
    for i in tiponota:
        tiponota2 = tiponota2 + "," + i

    tiponota2 = tiponota2[1:]

    # 1 - Carregar Os pedidos (etapa 1)
    pedidos = Monitor_CapaPedidos(empresa, iniVenda, finalVenda, tiponota2)
    pedidosBloqueados = Monitor_PedidosBloqueados()

    pedidos = pd.merge(pedidos,pedidosBloqueados,on='codPedido',how='left')
    pedidos['situacaobloq'].fillna('Liberado',inplace=True)
    pedidos = pedidos[pedidos['situacaobloq'] == 'Liberado']

    return pedidos





