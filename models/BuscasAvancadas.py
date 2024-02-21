# Velocidade de pesquisa

## SQL BUSCANDO AS ORDEM DE PRODUCAO EM ABERTO - velocidade media: 0,600 s (otima)


OP_emAberto = 'SELECT dataInicio as startOP, codProduto  , ' \
              'numeroOP , codTipoOP , codFaseAtual as codFase , seqAtual, codPrioridadeOP, codLote , codEmpresa ' \ 
               'FROM tco.OrdemProd o '\
               'WHERE o.codEmpresa = 1 and o.situacao = 3'



## SQL BUSCANDO AS " DATA/HORA DE MOVIMENTACAO DAS ORDEM DE PRODUCAO EM ABERTO " - velocidade media: 4,500 s (regular)

DataMov = 'SELECT numeroOP, dataMov , horaMov , seqRoteiro, (seqRoteiro + 1) as seqAtual FROM tco.MovimentacaoOPFase mf '\
            ' WHERE  numeroOP in (SELECT o.numeroOP from  tco.OrdemProd o' \
            ' WHERE o.codEmpresa = 1 and o.situacao = 3) and mf.codempresa = 1'

