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

@app.route('/pcp/api/Usuarios', methods=['PUT'])
@token_required
def criar_usuario():
    # Obtenha os dados do corpo da requisição
    novo_usuario = request.get_json()
    # Extraia os valores dos campos do novo usuário
    codigo = novo_usuario.get('codigo')
    nome = novo_usuario.get('nome')
    senha = novo_usuario.get('senha')
    # inserir o novo usuário no banco de dados
    c = Usuarios.ObterUsuariosCodigo(codigo)
    if c != 0:
        return jsonify({'message': f'Novo usuário:{codigo}- {nome} ja existe'}), 201
    else:
        Usuarios.InserirUsuario(codigo, nome, senha)
        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'message': f'Novo usuário:{codigo}- {nome} criado com sucesso'}), 201

@app.route('/pcp/api/Usuarios/<int:codigoUsuario>', methods=['DELETE'])
@token_required
def delet_Usuario(codigoUsuario):
    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoUsuario = str(codigoUsuario)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    dados = Usuarios.DeletarUsuarios(codigoUsuario)
    # Obtém os nomes das colunas
    column_names = dados.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    end_data = []
    for index, row in dados.iterrows():
        end_dict = {}
        for column_name in column_names:
            end_dict[column_name] = row[column_name]
        end_data.append(end_dict)
    return jsonify(end_data)

@app.route('/pcp/api/Usuarios/<int:codigo>', methods=['POST'])
@token_required
def update_usuario(codigo):
    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigo = str(codigo)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    codigo, nome_ant, senha_ant = Usuarios.ObterUsuariosCodigo(codigo)
    if codigo == 0:
        return jsonify({'message': f'Dados do Usuário {codigo} usuario nao existe! ', 'Status': False})
    else:
        if 'nome' in data:
            nome_novo = data['nome']
        else:
            nome_novo = nome_ant
        if 'senha' in data:
            senha_nova = data['senha']
        else:
            senha_nova = senha_ant
        Usuarios.EditarUsuario(codigo, nome_novo, senha_nova)

        return jsonify({'message': f'Dados do Usuário {codigo} - {nome_novo} atualizado com sucesso'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

