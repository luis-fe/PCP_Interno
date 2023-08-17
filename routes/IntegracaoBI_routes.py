from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import IntegracaoBI, ResponsabilidadeFase, ObterInfCSW, itens

integracaoBI = Blueprint('integracaoBI_routes', __name__)

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
def IntensBI():
    usuarios = itens.ItensCSW()
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