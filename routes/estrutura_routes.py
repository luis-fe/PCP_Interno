from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS
from models import Estrutura
import pandas as pd

estrutura_routes = Blueprint('estrutura_routes', __name__)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function
@estrutura_routes.route('/pcp/api/Estrutura', methods=['POST'])
@token_required
def get_Estrutura():
    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    plano = data.get('plano')
    codEngenharias = data.get('codEngenharias', '0')
    codMP = data.get('codMP', '0')
    nomeComponente = data.get('nomeComponente', '0')
    fornecedor = data.get('nomeFornecedor', '0')
    TamanhoProduto = data.get('TamanhoProduto', '0')
    desproduto = data.get('desproduto', '0')
    Excel = data.get('Excel', False)
    pagina = data.get('pagina', 0)  # Valor padrão: False, se 'estornar' não estiver presente no corpo
    itensPag = data.get('itensPag', 0)  # Valor padrão: False, se 'estornar' não estiver presente no corpo
    client_ip = request.remote_addr


    Endereco_det = Estrutura.Estrutura(client_ip, plano, pagina, itensPag, codEngenharias, str(codMP), nomeComponente, Excel, TamanhoProduto, fornecedor, desproduto)

    Endereco_det = pd.DataFrame(Endereco_det)

    # Obtém os nomes das colunas
    column_names = Endereco_det.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    end_data = []
    for _, row in Endereco_det.iterrows():
        end_dict = {column_name: row[column_name] for column_name in column_names}
        end_data.append(end_dict)

    return jsonify(end_data)
