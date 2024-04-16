"""
ARQUIVO USADO PARA CRIAR A ROTAS DO MONITOR DE FATURAMENTO
"""

from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import Estrutura, monitorFaturamento
import pandas as pd


monitorPreFaturamento_routes = Blueprint('monitor_routes', __name__)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function

@monitorPreFaturamento_routes.route('/pcp/api/monitorPreFaturamento', methods=['GET'])
@token_required
def get_monitorPreFaturamento():
    dados = request.get_json()
    empresa = dados.get('empresa')
    iniVenda = dados.get('iniVenda')
    finalVenda =dados.get('finalVenda')
    tiponota = dados.get('tiponota')
    print(tiponota.type)
    usuarios = monitorFaturamento.MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota)

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



