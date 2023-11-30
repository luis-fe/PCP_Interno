from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import dashbordTVModel, Vendas
import pandas as pd

dashboardTVroute = Blueprint('dashboardTVroute', __name__)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function
@dashboardTVroute.route('/pcp/api/dashboarTVBACKUP', methods=['GET'])
@token_required
def dashboarTVBACKUP():
    ano = request.args.get('ano','2023')
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
@token_required
def dashboarTV():
    ano = request.args.get('ano','2023')
    empresa = request.args.get('empresa', 'Todas')

    usuarios = dashbordTVModel.Faturamento_ano(ano,empresa)
    usuarios = pd.DataFrame(usuarios)




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
@dashboardTVroute.route('/pcp/api/metasFaturamento', methods=['GET'])
@token_required
def metasFaturamento():
    ano = request.args.get('ano','2023')
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