import pandas as pd
import ConexaoCSW
from datetime import datetime
import datetime
import pytz
import ConexaoPostgreMPL
import BuscasAvancadas
import re
import locale

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
def OPemProcesso(empresa, AREA, filtro = '-', filtroDiferente = '', tempo = 9999, limite = 60, classificar = '-'):
    filtro = filtro.upper()

    if (filtro == '-' and filtroDiferente == '' and tempo >= limite  ) or (filtro == '' and filtroDiferente == '' and tempo >= limite)   :
        conn = ConexaoCSW.Conexao()  # Conexao aberta do CSW

        # Etapa Trazendo as OP'em aberto, bem como as suas caracteristicas
        OP_emAberto = pd.read_sql(BuscasAvancadas.OP_Aberto(), conn)
        # Etapa Tratando a informacao da Descricao do Lote para o formato COLECAO
        OP_emAberto['lote'] = OP_emAberto['lote'].astype(str)
        OP_emAberto['lote'].fillna('-',inplace=True)
        OP_emAberto['COLECAO'] = OP_emAberto['lote'].apply(TratamentoInformacaoColecao)
        OP_emAberto['COLECAO'] = OP_emAberto['COLECAO'] + ' ' + OP_emAberto['lote'].apply(extrair_ano)


        OP_emAberto['seqAtual'] = OP_emAberto['seqAtual'].astype(str)
        OP_emAberto['codTipoOP'] = OP_emAberto['codTipoOP'].astype(str)

        tipoOP = pd.read_sql(BuscasAvancadas.TipoOP(), conn)
        tipoOP['codTipoOP'] = tipoOP['codTipoOP'].astype(str)

        OP_emAberto = pd.merge(OP_emAberto,tipoOP,on='codTipoOP', how='left')
        OP_emAberto['codTipoOP'] = OP_emAberto['codTipoOP'] +'-'+ OP_emAberto['nomeTipoOp']


        DataMov = pd.read_sql(BuscasAvancadas.DataMov(AREA), conn)
        DataMov['seqAtual'] = DataMov['seqAtual'].astype(str)

        consulta = pd.merge(OP_emAberto,DataMov,on=['numeroOP','seqAtual'], how='left')

        terceiros = pd.read_sql(BuscasAvancadas.OPporTecerceirizado(),conn)
        terceiros['codFase'] = terceiros['codFase'].astype(str)

        consulta = pd.merge(consulta, terceiros, on=['numeroOP','codFase'], how='left')

        requisicoes = pd.read_sql(BuscasAvancadas.RequisicoesOPs(), conn)
        partes = pd.read_sql(BuscasAvancadas.LocalizarPartesOP(), conn)


        partes['nomeParte']= partes.apply(
            lambda row: NomePartes(row['nomeParte'],'BORDADO','Parte Bordado'), axis=1)

        partes['nomeParte']= partes.apply(
            lambda row: NomePartes(row['nomeParte'],'COSTAS','Parte SilkCostas'), axis=1)

        partes['nomeParte']= partes.apply(
            lambda row: NomePartes(row['nomeParte'],'SILK','Parte Silk'), axis=1)

        partes['codNatEstoque'] = partes['nomeParte']+':'+partes['codNatEstoque']
        partes.drop('nomeParte', axis=1, inplace=True)

        partes['sitBaixa'] = partes.apply(lambda row: '🟢bx' if row['sitBaixa'] == '2' else '🔴ab.' , axis=1)





        requisicoes['fase'] = requisicoes['fase'].astype(str)
        requisicoes = requisicoes[requisicoes['fase'] == '425']
        requisicoes['sitBaixa'].fillna('ab.',inplace=True)
        requisicoes['sitBaixa'] = requisicoes.apply(lambda row: '🟢bx' if row['sitBaixa'] == '1' else '🔴ab.' , axis=1)
        requisicoes['codNatEstoque'] = requisicoes.apply(lambda row: 'avi.' if row['codNatEstoque'] == 1 else row['codNatEstoque'],
                                                    axis=1)
        requisicoes['codNatEstoque'] = requisicoes.apply(lambda row: 'golas' if row['codNatEstoque'] == 2 else row['codNatEstoque'],
                                                    axis=1)
        requisicoes['codNatEstoque'] = requisicoes.apply(lambda row: 'setor' if row['codNatEstoque'] == 3 else row['codNatEstoque'],
                                                    axis=1)
        requisicoes['numero'] = requisicoes['numero'].astype(str)
        requisicoes['sitBaixa'] = requisicoes['numero']+requisicoes['sitBaixa']
        # xx Nesse etapa é concatenado os dataframes Requsicao + Partes.
        requisicoes = pd.concat([requisicoes, partes], ignore_index=True)
        # xx Nessa etapa é excluida as colunas "fase" e "numero" para dar uma limpada no dataframe, deixando mais limpo.
        requisicoes.drop(['fase','numero'], axis=1, inplace=True)


        # Agrupando e criando a coluna 'detalhado'
        requisicoes = requisicoes.groupby('numeroOP').apply(
            lambda x: ', '.join(f"{codNatEstoque}{sitBaixa}" for codNatEstoque, sitBaixa in zip(x['codNatEstoque'], x['sitBaixa']))).reset_index(
            name='detalhado')
        #
        requisicoes['estaPendente'] = requisicoes.apply(lambda row: substituir_bx(row['detalhado']), axis=1)
        requisicoes['estaPendente'] = requisicoes['estaPendente'].str.replace('🔴ab.','')
        # Dividir a string em partes usando a vírgula como delimitador
        requisicoes['estaPendente'] = requisicoes.apply(lambda row: row['estaPendente'].split(','), axis=1)
        requisicoes['estaPendente'] = requisicoes.apply(lambda row: list(filter(bool, row['estaPendente'])), axis=1)


        requisicoes['Status Aguardando Partes'] = requisicoes.apply(lambda row: f'PENDENTE' if 'ab.' in row["detalhado"] else
                                                     f'OK' , axis=1)

        requisicoes['replicar'] = 'replicar'
        consulta['replicar'] = consulta.apply(lambda row: 'replicar' if row['codFase'] == '425' or row['codFase'] == '426' or row['codFase'] == '406'   else '-',
                                                    axis=1)

        consulta = pd.merge(consulta, requisicoes, on=['numeroOP', 'replicar'], how='left')


        justificativa = pd.read_sql('SELECT CONVERT(varchar(12), codop) as numeroOP, codfase as codFase, textolinha as justificativa1 FROM tco.ObservacoesGiroFasesTexto  t '
                                    'having empresa = 1 and textolinha is not null',conn)
        justificativa = justificativa.groupby(['numeroOP','codFase'])['justificativa1'].apply(' '.join).reset_index()

        justificativa['codFase'] = justificativa['codFase'].astype(str)


        conn2 = ConexaoPostgreMPL.conexao()
        justificativa2 = pd.read_sql('select ordemprod as "numeroOP", fase as "codFase", justificativa as justificativa2 from "PCP".pcp.justificativa ',conn2)
        leadTime2 = pd.read_sql('select categoria, codfase as "codFase", leadtime as meta2, limite_atencao from "PCP".pcp.leadtime_categorias ',conn2)
        conn2.close()

        conn3 = ConexaoPostgreMPL.conexao2()

        pcs = pd.read_sql(
            'select numeroop as "numeroOP", total_pcs as "Qtd Pcs" from "Reposicao".off.ordemprod ',
            conn3)
        #def format_with_separator(value):

         #       return locale.format('%0.0f', value, grouping=True)

        #pcs['Qtd Pcs'] = pcs['Qtd Pcs'].apply(format_with_separator)

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

        # Aqui fazemos o de-para para achar a categoria das partes filhas 
        deparaPartes = pd.read_sql(BuscasAvancadas.DeParaFilhoPaiCategoria(),conn)

        consulta = pd.merge(consulta,deparaPartes,on='codProduto',how='left')
        consulta['descricaoPai'].fillna('-',inplace=True)
        consulta['descricao'] = consulta.apply(lambda row: row['descricao'] if row['descricaoPai'] == '-' else row['descricaoPai'], axis=1)

        conn.close()  ## Conexao finalizada

        pcs.fillna(0, inplace=True)

        consulta = pd.merge(consulta,pcs,on='numeroOP', how='left')



        responsabilidade = ResponsabilidadeFases()
        consulta = pd.merge(consulta,responsabilidade,on='codFase', how='left')
        consulta = ExecoesResponsalFases(consulta,'412','4-PARTE KIT/CONJ')



        consulta = pd.merge(consulta,leadTime,on='codFase', how='left')


        consulta['data_entrada'].fillna('-',inplace=True)
        consulta['data_entrada'] = consulta.apply(lambda row: row['startOP'] if row['data_entrada'] == '-'  else row['data_entrada'] , axis=1)
        consulta = consulta[consulta['data_entrada'] != '-']
        consulta["prioridade"].fillna('NORMAL', inplace=True)
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
        consulta['prioridade'] = consulta.apply(lambda row: '1-URGENTE' if row['prioridade'] == 'URGENTE' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '09-P/FAT.' if row['prioridade'] == 'P/FATURAMENTO' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '09-P/FAT.' if 'FATURAMENTO' in row['prioridade'] else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '08-QP1' if row['prioridade'] == 'QP1' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '08-QM1' if row['prioridade'] == 'QM1' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '07-QP2' if row['prioridade'] == 'QP2' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '07-QM2' if row['prioridade'] == 'QM2' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '06-QP3' if row['prioridade'] == 'QP3' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '06-QM3' if row['prioridade'] == 'QM3' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '05-QP4' if row['prioridade'] == 'QP4' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '05-QM4' if row['prioridade'] == 'QM4' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '04-QP5' if row['prioridade'] == 'QP5' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '04-QM5' if row['prioridade'] == 'QM5' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '03-QP6' if row['prioridade'] == 'QP6' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '03-QM6' if row['prioridade'] == 'QM6' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '02-QP7' if row['prioridade'] == 'QP7' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '02-QM7' if row['prioridade'] == 'QM7' else row['prioridade'],axis=1 )
        consulta['prioridade'] = consulta.apply(lambda row: '01-NORMAL' if row['prioridade'] == 'NORMAL' else row['prioridade'],axis=1 )


        consulta['prioridade'] = consulta.apply(lambda row: '01-'+row['prioridade'] if '-' not in row['prioridade'] else row['prioridade'],axis=1 )


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

        consulta['nome'] = consulta.apply(
            lambda row: ApelidoFaccionista(row['nome'], 'CLAUDIANA', '(CLAUDIANA)'), axis=1)

        consulta['nome'] = consulta.apply(
            lambda row: ApelidoFaccionista(row['nome'], 'LPS', '( LPS)'), axis=1)
        consulta['nome'] = consulta.apply(
            lambda row: ApelidoFaccionista(row['nome'], 'BELLA D', '( DEVANI)'), axis=1)
        consulta['nome'] = consulta.apply(
            lambda row: ApelidoFaccionista(row['nome'], 'PATRICIO', '(PATRICIO)'), axis=1)
        consulta['nome'] = consulta.apply(
            lambda row: ApelidoFaccionista(row['nome'], 'PRODUZIR', '(PRODUZIR)'), axis=1)


        consulta['nome'] = consulta['nome'].replace('(-)','')
        consulta['nomeFase'] = consulta['nomeFase'] +' '+ consulta['nome']



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


        if classificar == 'tempo':
            consulta = consulta.sort_values(by=['dias na Fase'], ascending=False)  # escolher como deseja classificar

        elif classificar == 'status':
            consulta = consulta.sort_values(by=['status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        elif classificar == 'prioridade':
            print('deu certo: gerado ')
            consulta = consulta.sort_values(by=['prioridade','status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        else:
            consulta= consulta


        consulta['filtro'] = consulta['prioridade']+consulta['codProduto']+consulta['categoria']+consulta['codFase']+'-'+consulta['nomeFase']+consulta['numeroOP']+consulta['responsavel']+consulta['status']
        consulta['filtro'] = consulta['filtro'].str.replace(' ', '')
        consulta['filtro'] = consulta['filtro'].str.replace('-001', '')
        consulta['filtro'] = consulta['filtro'].str.replace('-2-Atrasado', 'ATRASADO')

        consulta.drop(['justificativa2','justificativa1','seqRoteiro','seqAtual','nomeTipoOp','replicar'], axis=1, inplace=True)

        consulta = consulta[(consulta['codFase'] != '426') | (consulta['codTipoOP'] != '2-PARTE DE PECA')]

        consulta.to_csv('cargaOP.csv',index=True)

        #Retirar o "-" da prioridade :
        consulta['prioridade'] = consulta['prioridade'] .str.split('-').str[1]

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
    elif filtro == '-' or filtro == '':

        consulta = pd.read_csv('cargaOP.csv')
        consulta.fillna('-', inplace=True)
        ##Converter string para lista
        #consulta['estaPendente'] = consulta['estaPendente'].apply(ast.literal_eval)
        consulta['estaPendente'] = consulta['estaPendente'].str.replace("[","")
        consulta['estaPendente'] = consulta['estaPendente'].str.replace("]", "")
        consulta['estaPendente'] = consulta.apply(lambda row: row['estaPendente'].split(','), axis=1)

        consulta = consulta[consulta['Area'] == AREA]


        if classificar == 'tempo':
            consulta = consulta.sort_values(by=['dias na Fase'], ascending=False)  # escolher como deseja classificar

        elif classificar == 'status':
            consulta = consulta.sort_values(by=['status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        elif classificar == 'prioridade':
            print('deu certo: buscou do que ta salvo')
            consulta = consulta.sort_values(by=['prioridade','status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        else:
            consulta= consulta

        consulta.drop('filtro', axis=1, inplace=True)

        consulta['Qtd Pcs'] = consulta['Qtd Pcs'].replace('-', 0)
        consulta['Qtd Pcs'].fillna(0,inplace= True)
        consulta['Qtd Pcs'] = consulta['Qtd Pcs'].astype(float)
        # Retirar o "-" da prioridade :
        consulta['prioridade'] = consulta['prioridade'].str.split('-').str[1]

        QtdPcs = consulta['Qtd Pcs'].sum()

        QtdPcs = "{:,.0f}".format(QtdPcs)
        QtdPcs = QtdPcs.replace(',', '')

        totalOP = consulta['numeroOP'].count()
        totalOP = "{:,.0f}".format(totalOP)
        totalOP = totalOP.replace(',', '')

        Atrazado = consulta[consulta['status'] == '2-Atrasado']
        totalAtraso = Atrazado['numeroOP'].count()
        totalAtraso = "{:,.0f}".format(totalAtraso)
        totalAtraso = totalAtraso.replace(',', '')

        Atencao = consulta[consulta['status'] == '1-Atencao']
        totalAtencao = Atencao['numeroOP'].count()
        totalAtencao = "{:,.0f}".format(totalAtencao)
        totalAtencao = totalAtencao.replace(',', '')

        dados = {
        '0-Total DE pçs':f'{QtdPcs} Pçs',
        '1-Total OP':f'{totalOP} Ops',
        '2- OPs Atrasadas':f'{totalAtraso} Ops',
        '2.1- OPs Atencao': f'{totalAtencao} Ops',
        '3 -Detalhamento':consulta.to_dict(orient='records')

        }
        return pd.DataFrame([dados])
    #essa etapa busca do que ta salvo
    else:
        filtros = pd.read_csv('cargaOP.csv')
        filtros = filtros[filtros['Area']== AREA]

        # Dividir a string em partes usando a vírgula como delimitador
        filtros['estaPendente'] = filtros['estaPendente'].str.replace("[","")
        filtros['estaPendente'] = filtros['estaPendente'].str.replace("]", "")
        filtros['estaPendente'] = filtros['estaPendente'].str.replace("'", "")

        filtros['estaPendente'] = filtros.apply(lambda row: row['estaPendente'].split(','), axis=1)


    ### ETAPA X : PROCEDIMENTO DE VARREDURA DOS TIPOS DE FILTRO INFORMADO PELO USUARIO:
    ###     NIVEL 1: NAO FILTRA O DATAFRAME, NIVEL2: FILTRA O DATAFRAME:

        matrizNivel = filtro.split("/")
        nivel1Array = []
        nivel2Array = []
        for busca in matrizNivel :
            nivel = ReconhecerFiltro(busca)

            if nivel == 'N2':
                nivel2Array.append(busca)
            else:
                nivel1Array.append(busca)

        ## Verifica se existe algum filtro de nivel2 para fazer uma filtragem nos dados
        if len(nivel2Array) == 0:
                print("sem filtro de nivel 2")
        else:
                filtrarValor = nivel2Array[0]
                print(f'filtro de nivel 2 encontrado: {filtrarValor}')
                filtros = filtros[filtros['filtro'].str.contains(filtrarValor)]

    ### FIM ETAPA X.


        if filtroDiferente == '':
            print(nivel1Array)

            filtrosNovo = None
            contador = 0


            for i in nivel1Array:
                contador = 1 + contador

                filtrosNovoCadeia = filtros[filtros['filtro'].str.contains(i)]
                if i == 1:
                    filtrosNovo = filtrosNovoCadeia
                else:

                    filtrosNovo = pd.concat([filtrosNovo, filtrosNovoCadeia],ignore_index=True)

        else:
            print(nivel1Array)
            filtroDif = filtros[~filtros['filtro'].str.contains(filtroDiferente)]

            filtrosNovo = None
            contador = 0
            for i in nivel1Array:
                contador = 1 + contador


                filtrosNovoCadeia = filtroDif[filtroDif['filtro'].str.contains(i)]
                if i == 1:
                    filtrosNovo = filtrosNovoCadeia
                else:

                    filtrosNovo = pd.concat([filtrosNovo, filtrosNovoCadeia],ignore_index=True)

        if classificar == 'tempo':
            filtrosNovo = filtrosNovo.sort_values(by=['dias na Fase'], ascending=False)  # escolher como deseja classificar

        elif classificar == 'status':
            filtrosNovo = filtrosNovo.sort_values(by=['status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        elif classificar == 'prioridade':
            print('deu certo: buscou do que ta salvo')
            filtrosNovo = filtrosNovo.sort_values(by=['prioridade','status','dias na Fase'], ascending=False)  # escolher como deseja classificar

        else:
            filtrosNovo= filtrosNovo




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

            filtrosNovo['Qtd Pcs'] = pd.to_numeric(filtrosNovo['Qtd Pcs'], errors='coerce').fillna(0).astype(int)
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

            filtrosNovo.fillna('-',inplace=True)


            filtrosNovo.drop(['filtro','Unnamed: 0'], axis=1, inplace=True)
            # Retirar o "-" da prioridade :
            filtrosNovo['prioridade'] = filtrosNovo['prioridade'].str.split('-').str[1]

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


def ApelidoFaccionista(entrada, referencia, saida):
    if referencia in entrada:
        return saida
    else:
        return entrada[0:9]

def NomePartes(entrada, referencia, saida):
    if referencia in entrada:
        return saida
    else:
        return entrada
# Função para extrair as informações desejadas
# Função para substituir "bx" por " " em cada conjunto de caracteres
def substituir_bx(conjunto):
    partes = [parte.strip() for parte in conjunto.split(',')]
    partes = ['' if 'bx' in parte else parte for parte in partes]
    return ','.join(partes)


def ReconhecerFiltro(filtro):
    palavras_chave = ['CAMI', 'CALCA', 'SHORT', 'BONE', 'POLO','JAQUET','ATRASA']

    if any(palavra in filtro for palavra in palavras_chave):
        return "N2"
    else:
        return 'N1'


def ExecoesResponsalFases(dataframe, fase, tipoop):
    dataframe['responsavel'] = dataframe.apply(lambda row: '' if row['codFase'] == fase and row['codTipoOP'] == tipoop else row['responsavel'], axis=1 )
    return dataframe


def TratamentoInformacaoColecao(descricaoLote):
    if 'INVERNO' in descricaoLote:
        return 'INVERNO'
    elif 'PRI' in descricaoLote:
        return 'VERAO'
    elif 'ALT' in descricaoLote:
        return 'ALTO VERAO'
    elif 'VER' in descricaoLote:
        return 'VERAO'
    else:
        return 'ENCOMENDAS'

def extrair_ano(descricaoLote):
    match = re.search(r'\b2\d{3}\b', descricaoLote)
    if match:
        return match.group(0)
    else:
        return None