import ConexaoCSW
import pandas as pd
import numpy



def Roteiro(like, empresa, ini, fim):
    like = "'"+like+"%'"

    ini = int(ini)
    fim = int(fim)

    if ini ==  0:
        conn = ConexaoCSW.Conexao()
        CapaOP = pd.read_sql('select  op.codLote, op.numeroOP, op.situacao, op.codFaseAtual, op.codSeqRoteiroAtual '
                            ' FROM tco.OrdemProd op '
                            ' WHERE op.codEmpresa = '+empresa+" and op.situacao > 1 and op.codLote like "+ like, conn )


        RoteiroOP = pd.read_sql('SELECT  r.numeroOP , r.codSeqRoteiro , r.codFase  from tco.RoteiroOP r '
                             ' WHERE r.codEmpresa = '+empresa+"  and r.codLote like "+ like, conn )

        DesdobramentoOP = pd.read_sql('select ot.numeroOP , ot.codItem, ot.codSortimento, ot.qtdePecas1Qualidade, ot.seqTamanho, ot.codProduto '
                             'FROM tco.OrdemProdTamanhos ot '
                             ' WHERE ot.codEmpresa = ' + empresa + "  and ot.codLote like " + like, conn)

        MovOP = pd.read_sql('SELECT f.codLote , f.numeroOP , f.codFase , f.seqRoteiro as codSeqRoteiro, f.dataMov, f.codFaccionista as faccionista_baixa  FROM tco.MovimentacaoOPFase f '
                             ' WHERE f.codEmpresa = '+empresa+"  and f.codLote like "+ like, conn )


        conn.close()

        CapaOP['codSeqRoteiroAtual']  = CapaOP['codSeqRoteiroAtual'] .replace('', numpy.nan).fillna('0')
        CapaOP.fillna('-', inplace=True)
        CapaOP['codSeqRoteiroAtual'] = CapaOP['codSeqRoteiroAtual'].astype(int)

        RoteiroOP['codFase'] = RoteiroOP['codFase'].astype(str)

        CapaOP = pd.merge(CapaOP, RoteiroOP, on='numeroOP')


        CapaOP["situacaoMovOP"] = CapaOP.apply(lambda row: 'em processo' if row['codFaseAtual'] == row['codFase']
            else '-', axis=1)

        CapaOP["situacaoMovOP"] = CapaOP.apply(lambda row: 'em fila'
        if row['situacaoMovOP'] != 'em processo' and row['codSeqRoteiro'] > row['codSeqRoteiroAtual']
            else row['situacaoMovOP'], axis=1)

        CapaOP["situacaoMovOP"] = CapaOP.apply(lambda row: 'movimentado'
        if row['situacaoMovOP'] == '-' or row['situacao']== '2'
            else row['situacaoMovOP'], axis=1)

        CapaOP = pd.merge(CapaOP, DesdobramentoOP, on='numeroOP')

        MovOP = MovOP.drop(['codLote','codFase'], axis=1)
        inicioPcp = MovOP[MovOP['codSeqRoteiro']==1]

        inicioPcp =  inicioPcp[['numeroOP','dataMov']]
        inicioPcp.rename(columns={'dataMov': 'inicioProducao'}, inplace=True)

        CapaOP = pd.merge(CapaOP, MovOP, on=['numeroOP','codSeqRoteiro'], how='left')
        CapaOP = pd.merge(CapaOP, inicioPcp, on=['numeroOP'])
        CapaOP = CapaOP.sort_values(by='inicioProducao', ascending=False)  # escolher como deseja classificar

        CapaOP['codProduto'] = CapaOP['codProduto'].replace('-0','')
        CapaOP['Id_reduzido'] =CapaOP['codProduto']+CapaOP['codSortimento']+CapaOP['seqTamanho']

        CapaOP.to_csv('roteiro_op.csv')

        CapaOP = CapaOP[0:fim]
        CapaOP.fillna('-', inplace=True)
        return CapaOP

    else:

        CapaOP = pd.read_csv('roteiro_op.csv')
        CapaOP = CapaOP[ini:fim]
        CapaOP.fillna('-', inplace=True)

        return CapaOP

def TamnhoDataFrame():
    CapaOP = pd.read_csv('roteiro_op.csv')
    tamanho = CapaOP['numeroOP'].size

    return pd.DataFrame([{'Mensagem':f'O tamanho do dataframe é {tamanho} linhas'}])




