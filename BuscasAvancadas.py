##################################### ARQUIVO.py UTILIZADO PARA CATALOGAR OS CODIGOS SQL DE BUSCA NO CSW: #########################################################

#Elaborado por : Luis Fernando Gonçalves de Lima Machado

## SQL BUSCANDO AS ORDEM DE PRODUCAO EM ABERTO - velocidade media da consulta : 0,850 s (otima)

def OP_Aberto():


    OP_emAberto = """
    SELECT (select pri.descricao  FROM tcp.PrioridadeOP pri WHERE pri.Empresa = 1 and o.codPrioridadeOP = pri.codPrioridadeOP ) as prioridade, dataInicio as startOP, codProduto  , numeroOP , codTipoOP , codFaseAtual as codFase , codSeqRoteiroAtual as seqAtual,
                  codPrioridadeOP, codLote , 
                  (select l.descricao as lote FROM tcl.Lote l WHERE l.codEmpresa = 1 and l.codlote = o.codlote  )as lote,
                  codEmpresa, (SELECT f.nome from tcp.FasesProducao f WHERE f.codempresa = 1 and f.codfase = o.codFaseAtual) as nomeFase, 
                  (select e.descricao from tcp.Engenharia e WHERE e.codempresa = o.codEmpresa and e.codengenharia = o.codProduto) as descricao
                  FROM tco.OrdemProd o 
                   WHERE o.codEmpresa = 1 and o.situacao = 3 
                   """

    return OP_emAberto
def PesquisarSequenciaRoteiro(codfase):
    consulta = """
    SELECT r.numeroOP , r.codSeqRoteiro as seq"""+codfase+""" FROM tco.RoteiroOP r
WHERE r.codEmpresa = 1 and r.codFase = """\
               + codfase+\
    """ and r.numeroOP in (select numeroOP from tco.OrdemProd op WHERE op.codempresa =1 and op.situacao = 3)
    """
    return consulta

def RequisicoesAbertas():
    consulta = """
    SELECT DISTINCT r.numOPConfec as numeroOP   from tcq.Requisicao r
WHERE r.codEmpresa = 1 and r.numOPConfec in (select numeroOP from tco.OrdemProd op WHERE op.codempresa =1 and op.situacao = 3)
and sitBaixa <> 1 and r.seqRoteiro <> 408 
    """
    return consulta


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
def CapaPedido (empresa, iniVenda, finalVenda, tiponota):
    empresa = "'"+str(empresa)+"'"

    CapaPedido = "SELECT   dataEmissao, convert(varchar(9), codPedido) as codPedido, "\
    "(select c.nome as nome_cli from fat.cliente c where c.codCliente = p.codCliente) as nome_cli, "\
    " codTipoNota, dataPrevFat, convert(varchar(9),codCliente) as codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo, qtdPecasFaturadas "\
    " FROM Ped.Pedido p"\
    " where codEmpresa = "+empresa+"  and  dataEmissao >= '" + iniVenda + "' and dataEmissao <= '" + finalVenda + "' and codTipoNota in (" + tiponota + ")  "

    return CapaPedido
def CapaPedidoPelaDataPrevOriginal (empresa, iniVenda, finalVenda, tiponota):
    empresa = "'"+str(empresa)+"'"

    CapaPedido = "SELECT   dataEmissao, convert(varchar(9), codPedido) as codPedido, "\
    "(select c.nome as nome_cli from fat.cliente c where c.codCliente = p.codCliente) as nome_cli, "\
    " codTipoNota, dataPrevFat, convert(varchar(9),codCliente) as codCliente, codRepresentante, descricaoCondVenda, vlrPedido as vlrSaldo, qtdPecasFaturadas "\
    " FROM Ped.Pedido p"\
    " where codEmpresa = "+empresa+"  and  dataPrevFat >= '" + iniVenda + "' and dataPrevFat <= '" + finalVenda + "' and codTipoNota in (" + tiponota + ")  "

    return CapaPedido

#SQL DE PEDIDOS NO NIVEL SKU - Velocidade Media 5 s para dados de 1 ano (regular)
def pedidosNivelSKU (empresa, iniVenda, finalVenda, tiponota):
    empresa = "'"+str(empresa)+"'"
    pedidosNivelSKU = 'select codPedido, codProduto as reduzido, qtdeCancelada, qtdeFaturada, qtdePedida '\
                        'from ped.PedidoItemGrade  p where codEmpresa = 1 and p.codPedido in '\
                        "(select p.codPedido FROM Ped.Pedido p where codEmpresa = 1 and dataEmissao >= '" + iniVenda + "' and dataEmissao <= '" + finalVenda + "')"

    return pedidosNivelSKU
#SQL DE BUSCA DE TERCEIRIZADOS POR OP E FASE - Velocidade Média: 0,700 s

def OPporTecerceirizado():
    OpTercerizados = 'SELECT CONVERT(VARCHAR(10), R.codOP) AS numeroOP, R.codFase as codFase, R.codFac,'\
  ' (SELECT nome  FROM tcg.Faccionista  f WHERE f.empresa = 1 and f.codfaccionista = r.codfac) as nome'\
 ' FROM TCT.RemessaOPsDistribuicao R'\
' INNER JOIN tco.OrdemProd op on'\
    ' op.codempresa = r.empresa and op.numeroop = CONVERT(VARCHAR(10), R.codOP)'\
    ' WHERE R.Empresa = 1 and op.situacao = 3 and r.situac = 2'

    return OpTercerizados

#SQL DEPARA DA ENGENHARIA PAI X FILHO: velocidade Média : 0,20 segundos

def DeParaFilhoPaiCategoria():

    dePara = "SELECT e.codEngenharia as codProduto,"\
     " (SELECT ep.descricao from tcp.Engenharia ep WHERE ep.codempresa = 1 and ep.codengenharia like '%-0' and '01'||SUBSTRING(e.codEngenharia, 3,9) = ep.codEngenharia) as descricaoPai"\
" FROM tcp.Engenharia e"\
" WHERE e.codEmpresa = 1 and e.codEngenharia like '6%' and e.codEngenharia like '%-0' and e.codEngenharia not like '65%'"

    return dePara

#SQL DE BUSCA DAS REQUISICOES DAS OPS : velocidade Média : 1,20 segundos

def RequisicoesOPs():

    requisicoes = """
    SELECT numero,numOPConfec as numeroOP ,  seqRoteiro as fase, sitBaixa, codNatEstoque
                  FROM tcq.Requisicao r WHERE r.codEmpresa = 1 and
                  r.numOPConfec in (SELECT op.numeroop from tco.OrdemProd op WHERE op.codempresa = 1 and op.situacao = 3)
    """

    return requisicoes

def RequisicaoOPsPartes():
    requisicao = """
        SELECT numero,codOPParte as numeroOP  ,  seqRoteiro as fase, sitBaixa, codNatEstoque
                  FROM tcq.Requisicao r 
                  inner join tco.RelacaoOPsConjuntoPartes p on p.codOPConjunto = r.numOPConfec 
                  WHERE r.codEmpresa = 1 and
                  r.numOPConfec in (SELECT op.numeroop from tco.OrdemProd op WHERE op.codempresa = 1 and op.situacao = 3)
    """
    return requisicao

#SQL DE BUSCA DAS PARTES DAS OPS : velocidade Média : 0,35 segundos (OTIMO)

def LocalizarPartesOP():

    partes = """
    SELECT p.codlote as numero, codopconjunto as numeroOP , '425' as fase, op.situacao as sitBaixa, codOPParte as codNatEstoque,
              (SELECT e.descricao from tcp.Engenharia e WHERE e.codempresa = 1 and e.codengenharia = op.codProduto) as nomeParte
              FROM tco.RelacaoOPsConjuntoPartes p
              inner join tco.OrdemProd op on op.codEmpresa = p.Empresa and op.numeroOP = p.codOPParte 
              WHERE codopconjunto in (SELECT op.numeroop from tco.OrdemProd op WHERE op.codempresa = 1 and op.situacao = 3 and op.codfaseatual = 426 )
              """

    return partes

#SQL DE BUSCA DAS MOVIMENTACOES ENTRE DATAS , TESTE COM 1 ANO : velocidade 9 segundos (REGULAR)
def MovimentacoesOps():
        dados = 'SELECT codFase, mf.numeroOP, dataMov as data_entrada, horaMov, mf.seqRoteiro, (mf.seqRoteiro + 1) as seqAtual FROM'\
                ' tco.MovimentacaoOPFase mf'\
                ' WHERE mf.codempresa = 1 and dataBaixa <= CURRENT_TIMESTAMP AND  '\
                " dataBaixa > DATEADD('day', -365, CURRENT_TIMESTAMP)"
        return dados

#SQL DE BUSCA DAS MOVIMENTACOES ENTRE DATAS no dia : velocidade 0,33 segundos (otimo)
def MovimentacoesOpsNodia():
        dados = 'SELECT codFase, mf.numeroOP, dataMov as data_entrada, horaMov, mf.seqRoteiro, (mf.seqRoteiro + 1) as seqAtual FROM'\
                ' tco.MovimentacaoOPFase mf'\
                ' WHERE mf.codempresa = 1 and dataBaixa <= CURRENT_TIMESTAMP AND  '\
                " dataBaixa > DATEADD('day', -1, CURRENT_TIMESTAMP)"
        return dados

def Motivos():
    motivos = 'SELECT codMotivo , nome FROM tcp.Mot2Qualidade m WHERE m.Empresa = 1'

    return motivos


def ObtendoEmbarqueUnico():

    df_Entregas_Solicitadas= """select top 100000 
                                         CAST(codPedido as varchar) as codPedido, 
                                         numeroEntrega as entregas_Solicitadas from asgo_ped.Entregas where 
                                         codEmpresa = 1  order by codPedido desc"""
    return df_Entregas_Solicitadas

def CapaSugestoes():
    consulta = """SELECT s.codPedido, p.codCondVenda, p.codTipoNota, p.codCliente, 
(SELECT  c.nome FROM fat.Cliente c where c.codempresa = 1 and c.codCliente = p.codCliente) as nomeCliente,
(SELECT  c.NOMEESTADO FROM fat.Cliente c where c.codempresa = 1 and c.codCliente = p.codCliente) as UF,
(SELECT  c.fantasia FROM fat.Cliente c where c.codempresa = 1 and c.codCliente = p.codCliente) as nomeFantasia
from ped.SugestaoPed s 
                            join ped.Pedido  p on  p.codEmpresa = s.codEmpresa and p.codPedido = s.codPedido  
                            where p.codEmpresa = 1 and s.situacaoSugestao = 0"""
    return consulta

def CondicoesDePGTO():
    consulta = """SELECT C.codigo as codCondVenda , C.descricao  FROM CAD.CondicaoDeVenda C WHERE C.codEmpresa = 1"""
    return consulta

def BuscarFaturamentoSugestoes():
    consulta = """SELECT n.codPedido, n.dataFaturamento  FROM fat.NotaFiscal n
WHERE n.codEmpresa = 1 
and n.codPedido > 0
and n.codPedido in (SELECT s.codpedido from ped.SugestaoPed s WHERE s.codempresa =1 )"""

    return consulta
def IncrementarPediosProdutos():
    consulta = """SELECT top 1000000 p.codPedido, p.codProduto , p.qtdePedida ,  p.qtdeFaturada, p.qtdeCancelada  FROM ped.PedidoItemGrade p
WHERE p.codEmpresa = 1 
order by codPedido desc"""

    return consulta

def SugestaoItemAberto():
    consulta = """SELECT p.codPedido , p.produto as codProduto , p.qtdeSugerida , p.qtdePecasConf  FROM ped.SugestaoPedItem p
WHERE p.codEmpresa = 1"""

    return consulta

def SituacaoPedidos():
    consulta = """SELECT * FROM (
SELECT top 300000 bc.codPedido, 'analise comercial' as situacaobloq  from ped.PedidoBloqComl  bc WHERE codEmpresa = 1  
and bc.situacaoBloq = 1
order by codPedido desc
UNION 
SELECT top 300000 codPedido, 'analise credito'as situacaobloq  FROM Cre.PedidoCreditoBloq WHERE Empresa  = 1  
and situacao = 1
order BY codPedido DESC) as D"""
    return consulta


def ConsultaEstoque():
    consulta = """select dt.reduzido as codProduto, SUM(dt.estoqueAtual) as estoqueAtual, sum(estReservPedido) as estReservPedido from
    (select codItem as reduzido, estoqueAtual,estReservPedido  from est.DadosEstoque where codEmpresa = 1 and codNatureza = 5 and estoqueAtual > 0)dt
    group by dt.reduzido
     """
    return consulta
def ConsultaEstoqueGarantidoPorFase():
    consulta = """select  ot.codItem as reduzido , ot.qtdePecas1Qualidade as estoqueAtual, 0 as estReservPedido  from Tco.OrdemProd o
    join Tco.OrdemProdTamanhos ot on ot.codEmpresa = o.codEmpresa and ot.numeroOP = o.numeroOP
    WHERE o.codEmpresa = 1 and o.situacao = 3 and o.codFaseAtual = '210' and ot.qtdePecas1Qualidade is not null and codItem is not null) dt
    group by dt.reduzido"""

    return consulta

def Entregas_Enviados():
    consulta= """select  top 300000 codPedido, count(codNumNota) as entregas_enviadas, 
                                      max(dataFaturamento) as ultimo_fat from fat.NotaFiscal  where codEmpresa = 1 and codRepresentante
                                      not in ('200','800','300','600','700','511') and situacao = 2 and codpedido> 0 and dataFaturamento > '2020-01-01' group by codPedido order by codPedido desc"""
    return consulta

def CapaSugestaoSituacao():

        consulta = """SELECT c.codPedido,situacaoSugestao as codSitSituacao ,
    case when (situacaoSugestao = 2 and dataHoraListagem>0) then 'Sugerido(Em Conferencia)' 
    WHEN situacaoSugestao = 0 then 'Sugerido(Gerado)' WHEN situacaoSugestao = 2 then 'Sugerido(Em Conferencia)' 
    WHEN situacaoSugestao = 1 then 'Sugerido(Gerado)' 
    else '' end StatusSugestao
    FROM ped.SugestaoPed c WHERE c.codEmpresa = 1  """

        return consulta

def ValorDosItensPedido():
    consulta = """select top 350000 item.codPedido, 
    item.CodItem as seqCodItem, 
    item.codProduto, 
    item.precoUnitario, item.tipoDesconto, item.descontoItem, 
    case when tipoDesconto = 1 then ( (item.qtdePedida * item.precoUnitario) - item.descontoItem)/item.qtdePedida when item.tipoDesconto = 0 then (item.precoUnitario * (1-(item.descontoItem/100))) else item.precoUnitario end  PrecoLiquido 
    from ped.PedidoItem as item WHERE item.codEmpresa = 1 order by item.codPedido desc """

    return consulta