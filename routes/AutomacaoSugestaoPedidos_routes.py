from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import reservaPrefaturamento
import pandas as pd
import subprocess

reservaPrefatroute = Blueprint('reservaPrefat', __name__)
CORS(reservaPrefatroute)


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function
@reservaPrefatroute.route('/pcp/api/ReservaPreFaturamento', methods=['GET'])
@token_required
def ReservaPreFaturamento():


    dataframe = reservaPrefaturamento.APIAtualizaPreFaturamento()

    # Obtém os nomes das colunas
    column_names = dataframe.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in dataframe.iterrows():
        op_dict = {}
        for index, row in dataframe.iterrows():
            op_dict = {}
            for column_name in column_names:
                op_dict[column_name] = row[column_name]
            OP_data.append(op_dict)
        return jsonify(OP_data)
