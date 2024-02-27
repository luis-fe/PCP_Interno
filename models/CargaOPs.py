import pandas as pd
import ConexaoCSW
from datetime import datetime
import datetime
import pytz
import ConexaoPostgreMPL
import BuscasAvancadas
def ResponsabilidadeFases():
    conn = ConexaoPostgreMPL.conexao()

    retorno = pd.read_sql('SELECT x.* FROM pcp."responsabilidadeFase" x ',conn)
    conn.close()

    return retorno

### Nesse documento é realizado o processo de buscar as OPs em aberto para exibir em dashboard
def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.datetime.now(fuso_horario)
    hora_str = agora.strftime('%Y-%m-%d %H:%M:%S')
    return hora_str



# Passo 1: Buscando as OP's em aberto no CSW
def OPemProcesso(empresa, AREA, filtro = '-'):

    if filtro == '-' or filtro == ''  :
        conn = ConexaoCSW.Conexao()  # Conexao aberta do CSW

        OP_emAberto = pd.read_sql(BuscasAvancadas.OP_Aberto(), conn)
        OP_emAberto['seqAtual'] = OP_emAberto['seqAtual'].astype(str)
        OP_emAberto['codTipoOP'] = OP_emAberto['codTipoOP'].astype(str)

        tipoOP = pd.read_sql(BuscasAvancadas.TipoOP(), conn)
        tipoOP['codTipoOP'] = tipoOP['codTipoOP'].astype(str)

        OP_emAberto = pd.merge(OP_emAberto,tipoOP,on='codTipoOP', how='left')
        OP_emAberto['codTipoOP'] = OP_emAberto['codTipoOP'] +'-'+ OP_emAberto['nomeTipoOp']


        DataMov = pd.read_sql(BuscasAvancadas.DataMov(AREA), conn)
        DataMov['seqAtual'] = DataMov['seqAtual'].astype(str)


        consulta = pd.merge(OP_emAberto,DataMov,on=['numeroOP','seqAtual'], how='left')

        justificativa = pd.read_sql('SELECT CONVERT(varchar(12), codop) as numeroOP, codfase as codFase, textolinha as justificativa1 FROM tco.ObservacoesGiroFasesTexto  t '
                                    'having empresa = 1 and textolinha is not null',conn)
        justificativa['codFase'] = justificativa['codFase'].astype(str)


        conn2 = ConexaoPostgreMPL.conexao()
        justificativa2 = pd.read_sql('select ordemprod as "numeroOP", fase as "codFase", justificativa as justificativa2 from "PCP".pcp.justificativa ',conn2)
        leadTime2 = pd.read_sql('select categoria, codfase as "codFase", leadtime as meta2, limite_atencao from "PCP".pcp.leadtime_categorias ',conn2)
        conn2.close()

        conn3 = ConexaoPostgreMPL.conexao2()

        pcs = pd.read_sql(
            'select numeroop as "numeroOP", total_pcs as "Qtd Pcs" from "Reposicao".off.ordemprod ',
            conn3)

        pcs['Qtd Pcs'].fillna(0, inplace=True)
        pcs['Qtd Pcs'] =pcs['Qtd Pcs'] .astype(int)
        pcs= pcs.groupby(['numeroOP']).agg({
            'Qtd Pcs':'sum'
        }).reset_index()
        conn3.close()






        # Concatenar os DataFrames
        consulta = pd.merge(consulta, justificativa2, on=['numeroOP','codFase'], how='left')
        consulta['justificativa2'].fillna('-',inplace=True)

        consulta = pd.merge(consulta, justificativa, on=['numeroOP','codFase'], how='left')
        consulta['justificativa1'].fillna('-',inplace=True)

        consulta['justificativa'] = consulta.apply(lambda row: row['justificativa2'] if row['justificativa2'] != '-' else row['justificativa1'], axis=1 )



        leadTime = pd.read_sql('SELECT f.codFase , f.leadTime as meta  FROM tcp.FasesProducao f WHERE f.codEmpresa = 1', conn)




        consulta['codFase'] = consulta['codFase'].astype(str)
        leadTime['codFase'] = leadTime['codFase'].astype(str)


        conn.close()  ## Conexao finalizada

        pcs.fillna(0, inplace=True)

        consulta = pd.merge(consulta,pcs,on='numeroOP', how='left')



        responsabilidade = ResponsabilidadeFases()
        consulta = pd.merge(consulta,responsabilidade,on='codFase', how='left')
        consulta = pd.merge(consulta,leadTime,on='codFase', how='left')
        consulta['data_entrada'].fillna('-',inplace=True)
        consulta['data_entrada'] = consulta.apply(lambda row: row['startOP'] if row['data_entrada'] == '-'  else row['data_entrada'] , axis=1)
        consulta = consulta[consulta['data_entrada'] != '-']
        consulta.fillna('-', inplace=True)

        consulta['data_entrada'] = consulta['data_entrada'].str.slice(0, 10)
        consulta['data_entrada'] = pd.to_datetime(consulta['data_entrada'], errors='coerce')


        # Verificando e lidando com valores nulos
        hora_str = obterHoraAtual()
        consulta['hora_str'] = hora_str
        consulta['hora_str'] = pd.to_datetime(consulta['hora_str'], errors='coerce')

        consulta['dias na Fase'] = (consulta['hora_str'] - consulta['data_entrada']).dt.days.fillna('')
        consulta['data_entrada'] = consulta['data_entrada'].astype(str)




        consulta.drop('hora_str', axis=1, inplace=True)
        consulta = consulta[consulta['dias na Fase'] != '']


        consulta['Area'] = consulta.apply(lambda row: 'PILOTO' if row['codTipoOP'] == '13-PILOTO' else 'PRODUCAO',axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '0-URGENTE' if row['prioridade'] == 'URGENTE' else '1-'+ row['prioridade'],axis=1 )


        consulta['categoria'] = '-'

        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CAMISA', row['descricao'], 'CAMISA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('POLO', row['descricao'], 'POLO', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('BATA', row['descricao'], 'CAMISA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('TRICOT', row['descricao'], 'TRICOT', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('BONE', row['descricao'], 'BONE', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CARTEIRA', row['descricao'], 'CARTEIRA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('TSHIRT', row['descricao'], 'CAMISETA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('REGATA', row['descricao'], 'CAMISETA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('BLUSAO', row['descricao'], 'AGASALHOS', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('BABY', row['descricao'], 'CAMISETA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('JAQUETA', row['descricao'], 'JAQUETA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CARTEIRA', row['descricao'], 'CARTEIRA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('BONE', row['descricao'], 'BONE', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CINTO', row['descricao'], 'CINTO', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('PORTA CAR', row['descricao'], 'CARTEIRA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('CUECA', row['descricao'], 'CUECA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('MEIA', row['descricao'], 'MEIA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('SUNGA', row['descricao'], 'SUNGA', row['categoria']), axis=1)
        consulta['categoria'] = consulta.apply(
            lambda row: Categoria('SHORT', row['descricao'], 'SHORT', row['categoria']), axis=1)


        consulta = pd.merge(consulta,leadTime2,on=['codFase','categoria'], how='left')

        ### Corrgindo as colunas para aceitar valores inteiros
        consulta['meta2'].fillna(0, inplace=True)
        consulta['meta2'] = consulta['meta2'].astype(int)

        consulta['meta'].fillna(0, inplace=True)
        consulta['meta'] = consulta['meta'].replace('-','0')
        consulta['meta'] = consulta['meta'].astype(int)

        consulta['limite_atencao'].fillna(0, inplace=True)
        consulta['limite_atencao'] = consulta['limite_atencao'].astype(int)

        consulta['dias na Fase'] = consulta['dias na Fase'].astype(int)

        ## Fim dessa etapa



        consulta['meta'] = consulta.apply(lambda row : row['meta'] if row['meta2'] == 0 else row['meta2'], axis=1)
        consulta.drop('meta2', axis=1, inplace=True)


        consulta['status'] = consulta.apply(lambda row: '2-Atrasado' if row['dias na Fase'] > row['meta'] else '0-Normal',axis=1 )
        consulta['status'] = consulta.apply(lambda row: '1-Atencao' if row['status'] == '2-Atrasado' and row['dias na Fase'] < row['limite_atencao']  else row['status'],axis=1 )

        consulta = consulta.sort_values(by=['prioridade','status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        consulta['filtro'] = consulta['codProduto']+consulta['data_entrada']+consulta['categoria']+consulta['codFase']+'-'+consulta['nomeFase']+consulta['numeroOP']+consulta['responsavel']+consulta['status']
        consulta['filtro'] = consulta['filtro'].str.replace(' ', '')

        consulta.drop(['justificativa2','justificativa1','seqRoteiro','seqAtual','nomeTipoOp'], axis=1, inplace=True)
        consulta.to_csv('cargaOP.csv',index=True)

        consulta = consulta[consulta['Area']== AREA]

        consulta.drop('filtro', axis=1, inplace=True)

        consulta['Qtd Pcs'] =consulta['Qtd Pcs'].replace('-',0)
        QtdPcs = consulta['Qtd Pcs'].sum()
        QtdPcs = "{:,.0f}".format(QtdPcs)
        QtdPcs = QtdPcs.replace(',','')

        totalOP = consulta['numeroOP'].count()
        totalOP = "{:,.0f}".format(totalOP)
        totalOP = totalOP.replace(',','')


        Atrazado = consulta[consulta['status'] == '2-Atrasado']
        totalAtraso =Atrazado['numeroOP'].count()
        totalAtraso = "{:,.0f}".format(totalAtraso)
        totalAtraso = totalAtraso.replace(',','')

        Atencao = consulta[consulta['status'] == '1-Atencao']
        totalAtencao =Atencao['numeroOP'].count()
        totalAtencao = "{:,.0f}".format(totalAtencao)
        totalAtencao = totalAtencao.replace(',','')


        dados = {
        '0-Total DE pçs':f'{QtdPcs} Pçs',
        '1-Total OP':f'{totalOP} Ops',
        '2- OPs Atrasadas':f'{totalAtraso} Ops',
        '2.1- OPs Atencao': f'{totalAtencao} Ops',
        '3 -Detalhamento':consulta.to_dict(orient='records')

        }


        return pd.DataFrame([dados])
    else:
        filtros = pd.read_csv('cargaOP.csv')
        filtros = filtros[filtros['Area']== AREA]

        array = filtro.split(",")

        filtrosNovo = filtros[filtros['filtro'].str.contains(filtro)]
        if filtrosNovo.empty:

            dados = {
                '0-Total DE pçs': '',
                '1-Total OP': '',
                '2- OPs Atrasadas': '',
                '2.1- OPs Atencao':'',
                '3 -Detalhamento': ''

            }

            return pd.DataFrame([dados])
        else:

            QtdPcs = filtrosNovo['Qtd Pcs'].sum()

            QtdPcs = str(QtdPcs).replace(',', '')

            totalOP = filtrosNovo['numeroOP'].count()
            totalOP = "{:,.0f}".format(totalOP)
            totalOP = totalOP.replace(',', '')

            Atrazado = filtrosNovo[filtrosNovo['status'] == '2-Atrasado']
            totalAtraso = Atrazado['numeroOP'].count()
            totalAtraso = "{:,.0f}".format(totalAtraso)
            totalAtraso = totalAtraso.replace(',', '')

            Atencao = filtrosNovo[filtrosNovo['status'] == '1-Atencao']
            totalAtencao = Atencao['numeroOP'].count()
            totalAtencao = "{:,.0f}".format(totalAtencao)
            totalAtencao = totalAtencao.replace(',', '')


            filtrosNovo.drop(['filtro','Unnamed: 0'], axis=1, inplace=True)

            dados = {
                '0-Total DE pçs': f'{QtdPcs} Pçs',
                '1-Total OP': f'{totalOP} Ops',
                '2- OPs Atrasadas': f'{totalAtraso} Ops',
                '2.1- OPs Atencao': f'{totalAtencao} Ops',
                '3 -Detalhamento': filtrosNovo.to_dict(orient='records')

            }

            return pd.DataFrame([dados])




def getCategoriaFases():

    conn = ConexaoPostgreMPL.conexao()

    sql = pd.read_sql('select * from "PCP".pcp.leadtime_categorias ',conn)

    conn.close()

    return sql

def Categoria(contem, valorReferencia, valorNovo, categoria):
    if contem in valorReferencia:
        return valorNovo
    else:
        return categoria




