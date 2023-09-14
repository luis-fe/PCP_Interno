from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import IntegracaoBI, ResponsabilidadeFase, ObterInfCSW, itens, op_csw, Vendas
import pandas as pd

integracaoBI = Blueprint('integracaoBI_routes', __name__)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function

@integracaoBI.route('/pcp/api/LoteBI', methods=['GET'])
def LoteBI():
    usuarios = IntegracaoBI.ConsultarLotesPlanos()
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

@integracaoBI.route('/pcp/api/FasesBI', methods=['GET'])
def FasesBI():
    usuarios = ResponsabilidadeFase.ObterFaseResponsais()
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

@integracaoBI.route('/pcp/api/IntensBI', methods=['GET'])
@token_required
def IntensBI():
    topItem = request.args.get('itens',10000)
    paginas = request.args.get('paginas',1)
    orderby = request.args.get('orderby', 'asc')
    data = request.args.get('dataInicial', '2015-01-01')

    usuarios = itens.ItensCSW(topItem, int(paginas),orderby,data)
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

@integracaoBI.route('/pcp/api/OPSBI', methods=['GET'])
def OPSBI():
    topItem = request.args.get('itens')
    paginas = request.args.get('paginas',1)
    data = request.args.get('anoLote', '23')

    usuarios = op_csw.ItensCSW(topItem, int(paginas),data)

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


@integracaoBI.route('/pcp/api/prioridadeFatBI', methods=['GET'])
def prioridadeFatBI():
    empresa = request.args.get('empresa','1')
    dataInicio = request.args.get('dataInicio','2023-06-01')
    dataFinal = request.args.get('dataFinal', '2024-01-01')
    calcular = request.args.get('calcular', 'True')

    if calcular == 'True':
        calculo = Vendas.PedidosAbertos(empresa, dataInicio,dataFinal)
    else:
        print('sem calcular')

    usuarios = Vendas.abrircsv()
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