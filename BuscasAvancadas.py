# Velocidade de pesquisa

## SQL BUSCANDO AS ORDEM DE PRODUCAO EM ABERTO - velocidade media: 0,850 s (otima)

def OP_Aberto():
    OP_emAberto = 'SELECT dataInicio as startOP, codProduto  , numeroOP , codTipoOP , codFaseAtual as codFase , codSeqRoteiroAtual as seqAtual, codPrioridadeOP, codLote , codEmpresa, '\ 
                   ' (SELECT f.nome from tcp.FasesProducao f WHERE f.codempresa = 1 and f.codfase = o.codFaseAtual) as nomeFase, ' \
                  '(select e.descricao from tcp.Engenharia e WHERE e.codempresa = o.codEmpresa and e.codengenharia = o.codProduto) as descricao' \
                  ' FROM tco.OrdemProd o '\
                   ' WHERE o.codEmpresa = 1 and o.situacao = 3'

    return OP_emAberto



## SQL BUSCANDO AS " DATA/HORA DE MOVIMENTACAO DAS ORDEM DE PRODUCAO EM ABERTO " - velocidade media: 4,500 s (regular)

def DataMov():
        DataMov = 'SELECT numeroOP, dataMov as data_entrada , horaMov , seqRoteiro, (seqRoteiro + 1) as seqAtual FROM tco.MovimentacaoOPFase mf '\
            ' WHERE  numeroOP in (SELECT o.numeroOP from  tco.OrdemProd o' \
            ' WHERE o.codEmpresa = 1 and o.situacao = 3) and mf.codempresa = 1'

        return DataMov

