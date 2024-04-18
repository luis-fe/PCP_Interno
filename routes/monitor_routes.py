"""
ARQUIVO USADO PARA CRIAR A ROTAS DO MONITOR DE FATURAMENTO
"""

from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import Estrutura, monitorFaturamento, controle
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

@monitorPreFaturamento_routes.route('/pcp/api/detalhadoMonitor', methods=['GET'])
@token_required
def detalhadoMonitor():
    empresa = request.args.get('empresa')
    iniVenda = request.args.get('iniVenda','-')
    finalVenda = request.args.get('finalVenda')
    tiponota = request.args.get('tiponota')
    rotina = 'detalhadoMonitor'
    client_ip = request.remote_addr
    datainicio = controle.obterHoraAtual()
    controle.InserindoStatus(rotina, client_ip, datainicio)

    usuarios = monitorFaturamento.MonitorDePreFaturamento(empresa, iniVenda, finalVenda, tiponota,rotina, client_ip, datainicio)
    controle.salvarStatus(rotina, client_ip, datainicio)
    usuarios = pd.DataFrame([{"Mensagem":"Salvo c/sucesso"}])

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


@monitorPreFaturamento_routes.route('/pcp/api/monitorPreFaturamento', methods=['GET'])
@token_required
def get_monitorPreFaturamento():
    empresa = request.args.get('empresa')
    iniVenda = request.args.get('iniVenda','-')
    finalVenda = request.args.get('finalVenda')
    tiponota = request.args.get('tiponota')

    rotina = 'monitorPreFaturamento'
    client_ip = request.remote_addr
    datainicio = controle.obterHoraAtual()
    controle.InserindoStatus(rotina, client_ip, datainicio)
    usuarios = monitorFaturamento.API(empresa, iniVenda, finalVenda, tiponota)
    controle.salvarStatus(rotina, client_ip, datainicio)

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
