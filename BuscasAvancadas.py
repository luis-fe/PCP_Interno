##################################### ARQUIVO.py UTILIZADO PARA CATALOGAR OS CODIGOS SQL DE BUSCA NO CSW: #########################################################

#Elaborado por : Luis Fernando Gonçalves de Lima Machado

## SQL BUSCANDO AS ORDEM DE PRODUCAO EM ABERTO - velocidade media da consulta : 0,850 s (otima)

def OP_Aberto():


    OP_emAberto = 'SELECT dataInicio as startOP, codProduto  , numeroOP , codTipoOP , codFaseAtual as codFase , codSeqRoteiroAtual as seqAtual, ' \
                  'codPrioridadeOP, codLote , codEmpresa, (SELECT f.nome from tcp.FasesProducao f WHERE f.codempresa = 1 and f.codfase = o.codFaseAtual) as nomeFase, ' \
                  '(select e.descricao from tcp.Engenharia e WHERE e.codempresa = o.codEmpresa and e.codengenharia = o.codProduto) as descricao' \
                  ' FROM tco.OrdemProd o '\
                   ' WHERE o.codEmpresa = 1 and o.situacao = 3'

    return OP_emAberto



## SQL BUSCANDO AS " DATA/HORA DE MOVIMENTACAO DAS ORDEM DE PRODUCAO EM ABERTO " - velocidade media: 4,500 s (regular)

def DataMov(AREA):

    if AREA == 'PRODUCAO':
        DataMov = 'SELECT numeroOP, dataMov as data_entrada , horaMov , seqRoteiro, (seqRoteiro + 1) as seqAtual FROM tco.MovimentacaoOPFase mf '\
            ' WHERE  numeroOP in (SELECT o.numeroOP from  tco.OrdemProd o' \
            ' having o.codEmpresa = 1 and o.situacao = 3 and o.codtipoop <> 13) and mf.codempresa = 1 order by codlote desc'
    else:
        DataMov = 'SELECT numeroOP, dataMov as data_entrada , horaMov , seqRoteiro, (seqRoteiro + 1) as seqAtual FROM tco.MovimentacaoOPFase mf '\
            ' WHERE  numeroOP in (SELECT o.numeroOP from  tco.OrdemProd o' \
            ' having o.codEmpresa = 1 and o.situacao = 3 and o.codtipoop = 13) and mf.codempresa = 1 order by codlote desc'

    return DataMov

# SQL BUSCAR OS TIPO's DE OP DO CSW
def TipoOP():

    TipoOP = 'SELECT t.codTipo as codTipoOP, t.nome as nomeTipoOp  FROM tcp.TipoOP t WHERE t.Empresa = 1'

    return TipoOP


# Sql Buscando Pedidos Bloqueados NO CREDITO tempo 0,100 ms (otimo)
def BloqueiosCredito():

    BloqueiosCredito = "SELECT codPedido, 'BqCredito' as situacao  FROM Cre.PedidoCreditoBloq WHERE Empresa = 1 and situacao = 1 "

    return BloqueiosCredito

# Sql Buscando Pedidos Bloqueados NO COMERCIAL tempo 0,050 ms (otimo)
def bloqueioComerical():
    bloqueioComerical = 'SELECT codPedido, situacaoBloq as situacao from ped.PedidoBloqComl c WHERE codEmpresa = 1 and situacaoBloq = 1 '

    return bloqueioComerical

# SQL CAPA DOS PEDIDOS: Velocidade media : 1,5 s (ótimo - para o intervalo de 1 ano de pedidos)
def CapaPedido (iniVenda, finalVenda, tiponota):

    CapaPedido = "SELECT dataEmissao, codPedido, "\
    "(select c.nome as nome_cli from fat.cliente c where c.codCliente = p.codCliente) as nome_cli, "\
    " codTipoNota, dataPrevFat, codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo,qtdPecasFaturadas "\
    " FROM Ped.Pedido p"\
    " where codEmpresa = 1 and  dataEmissao >= '" + iniVenda + "' and dataEmissao <= '" + finalVenda + "' and codTipoNota in (" + tiponota + ")"\
    " order by codPedido desc "

    return CapaPedido


#SQL DE PEDIDOS NO NIVEL SKU - Velocidade Media 5 s para dados de 1 ano (regular)
def pedidosNivelSKU (iniVenda, finalVenda, tiponota):
    pedidosNivelSKU = 'select codPedido, codProduto as reduzido, qtdeCancelada, qtdeFaturada, qtdePedida '\
                        'from ped.PedidoItemGrade  p where codEmpresa = 1 and p.codPedido in '\
                        "(select p.codPedido FROM Ped.Pedido p where codEmpresa = 1 and dataEmissao >= '" + iniVenda + "' and dataEmissao <= '" + finalVenda + ")"

    return pedidosNivelSKU
#SQL DE BUSCA DE TERCEIRIZADOS POR OP E FASE - Velocidade Média

#SQL DE BUSCA DA ESTRUTURA DE ITENS - PRODUTO ACABADO - Velocidade Média
