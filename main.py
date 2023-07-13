from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from functools import wraps
import ConexaoPostgreMPL
import Usuarios

app = Flask(__name__)
port = int(os.environ.get('PORT', 8000))
CORS(app)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function

# Rota protegida que requer o token fixo para trazer os Usuarios Cadastrados
# Rota pagina inicial
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/pcp/api/Usuarios', methods=['GET'])
@token_required
def get_Usuarios():
    usuarios = Usuarios.ObterUsuarios()
    # Obtém os nomes das colunas
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

