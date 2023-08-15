from flask import Blueprint,Flask, render_template, jsonify, request
from functools import wraps
from flask_cors import CORS

import Plano

plano_routes = Blueprint('plano_routes', __name__)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function

@plano_routes.route('/pcp/api/Plano', methods=['GET'])
@token_required
def get_Plano():
    plano = Plano.ObeterPlanos()
    # Obtém os nomes das colunas
    # Obtém os nomes das colunas
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)
@plano_routes.route('/pcp/api/ColecoesPlano/<string:codigoplano>', methods=['GET'])
@token_required
def get_ColecoesPlano(codigoplano):
    plano = Plano.ObeterColecoesPlano(codigoplano)
    # Obtém os nomes das colunas
    # Obtém os nomes das colunas
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@plano_routes.route('/pcp/api/NotasPlano/<string:codigoplano>', methods=['GET'])
@token_required
def get_NotasPlano(codigoplano):
    plano = Plano.ObeterNotasPlano(codigoplano)
    # Obtém os nomes das colunas
    # Obtém os nomes das colunas
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)

@plano_routes.route('/pcp/api/LotesPlano/<string:codigoplano>', methods=['GET'])
@token_required
def get_LotePlano(codigoplano):
    plano = Plano.ObeterLotesPlano(codigoplano)
    # Obtém os nomes das colunas
    # Obtém os nomes das colunas
    column_names = plano.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    OP_data = []
    for index, row in plano.iterrows():
        op_dict = {}
        for column_name in column_names:
            op_dict[column_name] = row[column_name]
        OP_data.append(op_dict)
    return jsonify(OP_data)
@plano_routes.route('/pcp/api/StatusPlano/<string:codigoPlano>', methods=['GET'])
@token_required
def Status_Plano(codigoPlano):
    # Obtém os dados do corpo da requisição (JSON)
    codigoPlano = str(codigoPlano)
    # inserir o novo usuário no banco de dados
    codigo2, descricaoAnt, iniVendaAnt, finalVendaAnt, inicioFatAnt, finalFatAnt= Plano.ConsultarPlano(codigoPlano)
    if codigo2 != 0:
        return jsonify({'00 message': f'Plano {codigoPlano}-{descricaoAnt} ja existe', '001 status':True,'01- Codigo Plano':codigoPlano
                       , '02- Descricao do Plano':descricaoAnt, '03- Inicio Venda':iniVendaAnt,
                        '04- Final Venda':finalVendaAnt,'05- Inicio Faturamento':inicioFatAnt,'06- Final Faturamento':finalFatAnt}), 201
    else:
        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'00 message': f'Plano {codigoPlano} nao existe', '001 status':False}), 201

@plano_routes.route('/pcp/api/Plano', methods=['PUT'])
@token_required
def criar_Plano():
    # Obtenha os dados do corpo da requisição
    novo_usuario = request.get_json()
    # Extraia os valores dos campos do novo usuário
    codigo = novo_usuario.get('codigo')
    descricao = novo_usuario.get('descricao')
    inicoVenda = novo_usuario.get('inicoVenda','-')
    finalVenda = novo_usuario.get('finalVenda','-')
    inicioFat = novo_usuario.get('inicioFat','-')
    finalFat = novo_usuario.get('finalFat','-')
    usuario = novo_usuario.get('usuario','-')
    dataGeracao = novo_usuario.get('dataGeracao','-')

    # inserir o novo usuário no banco de dados
    c, c2, c3, c4, c5, c6 = Plano.ConsultarPlano(codigo)

    if c != 0:
        return jsonify({'message': f'Plano {codigo}-{descricao} ja existe', 'status':False}), 201
    else:
        Plano.InserirPlano(codigo, descricao, inicoVenda,finalVenda,inicioFat,finalFat,usuario,dataGeracao)
        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'message': f'Plano {codigo}-{descricao} criado com sucesso', 'status':True}), 201
@plano_routes.route('/pcp/api/Plano/<string:codigoPlano>', methods=['DELETE'])
@token_required
def delet_Plano(codigoPlano):
    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    dados = Plano.DeletarPlano(codigoPlano)
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