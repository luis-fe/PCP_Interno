from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
import pandas as pd

from models import metaPlano

metaPlano_routes = Blueprint('metaPlano_routes', __name__)

@metaPlano_routes.route('/pcp/api/metaPlano/<string:codigoplano>', methods=['GET'])
def get_metaPlano(codigoplano):
    usuarios = metaPlano.Get_Consultar(codigoplano)
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
@metaPlano_routes.route('/pcp/api/metaPlanoSemanal/<string:codigoplano>', methods=['GET'])
def get_metaPlanoSemana(codigoplano):
    usuarios = metaPlano.metasSemanais(codigoplano)
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

@metaPlano_routes.route('/pcp/api/metaPlanoSemanal', methods=['POST'])
def metaPlanoSemanal():
    dados = request.get_json()
    plano = dados.get('plano')
    marca = dados.get('marca')
    semana =dados.get('semana')
    percentualDist = dados.get('percentualDist')

    usuarios = metaPlano.InserindoPercentual(plano, marca, semana, percentualDist)

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

@metaPlano_routes.route('/pcp/api/metaPlano', methods=['POST'])
def post_metaPlano():
    novo_usuario = request.get_json()
    codigoplano = novo_usuario.get('codigoplano')
    marca = novo_usuario.get('marca')
    metaPeca = novo_usuario.get('metaPeca')
    metaReais = novo_usuario.get('metaReais')

    usuarios = metaPlano.InserirMeta(codigoplano,marca,metaReais, metaPeca)
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

@metaPlano_routes.route('/pcp/api/metaPlano', methods=['PUT'])
def pUT_metaPlano():
    novo_usuario = request.get_json()
    codigoplano = novo_usuario.get('codigoplano')
    marca = novo_usuario.get('marca')
    metaPeca = novo_usuario.get('metaPeca')
    metaReais = novo_usuario.get('metaReais')

    usuarios = metaPlano.EditarMeta(codigoplano,marca,metaReais, metaPeca)
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