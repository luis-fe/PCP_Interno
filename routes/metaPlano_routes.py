from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS

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