from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import dashbordTVModel, Vendas, CargaOPs, justificativaOPFase, controle, outlet
import pandas as pd
import subprocess



dashboardTVroute = Blueprint('dashboardTVroute', __name__)
CORS(dashboardTVroute)


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function

@dashboardTVroute.route('/pcp/api/CargaOPs', methods=['POST'])
@token_required
def CargadasOPs():


    data = request.get_json()
    empresa = data.get('empresa','1')
    filtro = data.get('filtro', '-')
    area = data.get('area', 'PRODUCAO')
    filtroDiferente = data.get('filtroDiferente', '')
    rotina = 'Portal Consulta OP'
    classificar = data.get('classificar', '-')
    colecao = data.get('colecao','')

    if colecao == []:
        colecao = ''

    print(f'foi classficado por {classificar}')
    client_ip = request.remote_addr
    datainicio = controle.obterHoraAtual()
    tempo = controle.TempoUltimaAtualizacaoPCP(datainicio,rotina)
    limite = 60
    limiteFiltros = 600

    if (filtro == '-' and filtroDiferente == '' and tempo >= limite  ) or (filtro == '' and filtroDiferente == '' and tempo >= limite)  :
        usuarios = CargaOPs.OPemProcesso(empresa, area, filtro, filtroDiferente, tempo, limite,classificar,colecao)  ## Aqui defino que o tempo limite de requisicao no csw é acima de 60 segundos, evitando a simultanedade de requisicao
        controle.salvar('Portal Consulta OP',client_ip,datainicio)
        controle.ExcluirHistorico(3)

    elif tempo >= limiteFiltros :
        usuarios1 = CargaOPs.OPemProcesso(empresa, area, '-', '', tempo, limite,classificar,colecao)  ## Aqui defino que o tempo limite de requisicao no csw é acima de 60 segundos, evitando a simultanedade de requisicao

        controle.salvar('Portal Consulta OP',client_ip,datainicio)
        controle.ExcluirHistorico(3)
        usuarios = CargaOPs.OPemProcesso(empresa, area, filtro, filtroDiferente, tempo, limite,classificar,colecao)  ## Aqui defino que o tempo limite de requisicao no csw é acima de 60 segundos, evitando a simultanedade de requisicao


    else:
        usuarios = CargaOPs.OPemProcesso(empresa, area, filtro, filtroDiferente, tempo, limite,classificar,colecao)  ## Aqui defino que o tempo limite de requisicao no csw é acima de 60 segundos, evitando a simultanedade de requisicao
        print(client_ip+' '+filtro)

    # Obtém os nomes das colunas
    column_names = usuarios.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []

    for index, row in usuarios.iterrows():
        op_dict = {}
        for index, row in usuarios.iterrows():
            op_dict = {}
            for column_name in column_names:
                op_dict[column_name] = row[column_name]
            OP_data.append(op_dict)
        return jsonify(OP_data) , 200


def restart_server():
    print("Reiniciando o aplicativo...")
    subprocess.call(["python", "main.py"])
@dashboardTVroute.route('/pcp/api/dashboarTVBACKUP', methods=['GET'])
@token_required
def dashboarTVBACKUP():
    ano = request.args.get('ano','2024')
    empresa = request.args.get('empresa', 'Todas')

    usuarios = dashbordTVModel.Backup(ano,empresa)
    usuarios = pd.DataFrame([{'mensagem':f'Backup salvo com sucesso - empresa {empresa}'}])


    # Obtém os nomes das colunas
    column_names = usuarios.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in usuarios.iterrows():
        op_dict = {}
        for index, row in usuarios.iterrows():
            op_dict = {}
            for column_name in column_names:
                op_dict[column_name] = row[column_name]
            OP_data.append(op_dict)
        return jsonify(OP_data)


@dashboardTVroute.route('/pcp/api/dashboarTV', methods=['GET'])
def dashboarTV():
    try:
        ano = request.args.get('ano', '2024')
        empresa = request.args.get('empresa', 'Todas')

        if empresa == 'Outras':
            usuarios = dashbordTVModel.OutrosFat(ano, empresa)
            usuarios = pd.DataFrame(usuarios)
        else:
            usuarios = dashbordTVModel.Faturamento_ano(ano, empresa)
            usuarios = pd.DataFrame(usuarios)

        # Obtém os nomes das colunas
        column_names = usuarios.columns
        # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
        OP_data = []
        for index, row in usuarios.iterrows():
            op_dict = {}
            for column_name in column_names:
                op_dict[column_name] = row[column_name]
            OP_data.append(op_dict)

        return jsonify(OP_data)
    except Exception as e:
        print(f"Erro detectado: {str(e)}")
        restart_server()
        return jsonify({"error": "O servidor foi reiniciado devido a um erro."})


@dashboardTVroute.route('/pcp/api/metasFaturamento', methods=['GET'])
@token_required
def metasFaturamento():
    ano = request.args.get('ano','2024')
    empresa = request.args.get('empresa', '1')

    plano = dashbordTVModel.GetMetas(empresa,ano)
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@dashboardTVroute.route('/pcp/api/AcompVendas', methods=['GET'])
@token_required
def AcompVendas():
    plano = request.args.get('plano')
    empresa = request.args.get('empresa', '1')
    somenteAprovados = request.args.get('somenteAprovados', '')
    marca = request.args.get('marca', 'Geral')
    congelado = request.args.get('congelado', False)

    if congelado == 'False' or congelado == 'false' or congelado == '':
        congelado = False

    elif congelado == False:
        congelado = False

    else:
        congelado = True

    if somenteAprovados == 'False' or somenteAprovados == 'false' :
        somenteAprovados = 'False'
    elif somenteAprovados == 'True' or somenteAprovados == 'true':
        somenteAprovados = 'True'
    else:
        somenteAprovados = ''

    if marca == '':
        marca = 'Geral'
    else:
        marca = marca



    plano = Vendas.VendasPlano(plano,empresa,somenteAprovados,marca,bool(congelado))
    plano = pd.DataFrame(plano)
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)



@dashboardTVroute.route('/pcp/api/RelatorioVendas', methods=['GET'])
@token_required
def RelatorioVendas():
    plano = request.args.get('plano', '1')

    plano = Vendas.EmitirRelatorio(plano)
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@dashboardTVroute.route('/pcp/api/CadastrarJustificativa', methods=['PUT'])
@token_required
def CadastrarJustificativa():

    data = request.get_json()

    ordemProd = data.get('ordemProd', '-')
    fase = data.get('fase', '-')
    justificativa = data.get('justificativa', '-')

    plano = justificativaOPFase.CadastrarJustificativa(ordemProd, fase, justificativa)
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@dashboardTVroute.route('/pcp/api/ConsultarJustificativa', methods=['GET'])
@token_required
def ConsultarJustificativa():

    ordemProd = request.args.get('ordemProd')
    fase = request.args.get('fase', '-')

    plano = justificativaOPFase.ConsultarJustificativa(ordemProd, fase)
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@dashboardTVroute.route('/pcp/api/leadtimeCategorias', methods=['GET'])
@token_required
def leadtimeCategorias():


    plano = CargaOPs.getCategoriaFases()
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@dashboardTVroute.route('/pcp/api/outletVendas', methods=['GET'])
@token_required
def outletVendas():


    plano = outlet.AnaliseVendasOutlet()
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@dashboardTVroute.route('/pcp/api/DistinctColecao', methods=['GET'])
@token_required
def DistinctColecao():


    usuarios = CargaOPs.DistinctColecao()


    # Obtém os nomes das colunas
    column_names = usuarios.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in usuarios.iterrows():
        op_dict = {}
        for index, row in usuarios.iterrows():
            op_dict = {}
            for column_name in column_names:
                op_dict[column_name] = row[column_name]
            OP_data.append(op_dict)
        return jsonify(OP_data)