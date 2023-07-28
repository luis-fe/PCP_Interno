from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from functools import wraps
import ConexaoPostgreMPL
import Estrutura
import ObterInfCSW
import Plano
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
@app.route('/pcp/api/UsuarioSenha', methods=['POST'])
@token_required
def get_UsuarioSenha():
    # Obtém os dados do corpo da requisição (JSON)
    codigo = request.get_json()
    codigo = codigo.get('codigo')
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    codigo, nome , senha = Usuarios.ObterUsuariosCodigo(codigo)
    if codigo != 0:
        return jsonify({'1 - message': f'Usuario {codigo}- {nome}', '2-Senha': f'{senha}'}), 201
    else:

        return jsonify({'message': 'Usuario Nao existe'}), 201

@app.route('/pcp/api/UsuarioSenha', methods=['GET'])
@token_required
def get_UsuarioSenha_():
    # Obtém o código do usuário e a senha dos parâmetros da URL
    codigo = request.args.get('codigo')
    senhaP = request.args.get('senha')

    # Verifica se a coluna "funcao" está presente nos dados recebidos
    codigo, nome , senha = Usuarios.ObterUsuariosCodigo(codigo)
    if codigo != 0 and senha == senhaP:
        return jsonify({'1 - message': f'Usuario {codigo}- {nome}', '2-Senha': f'{senha}', "status": True, "Usuario":f'{codigo}'}), 201
    else:

        return jsonify({'message': 'Usuario OU senha Nao existe','status': False}), 201

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

@app.route('/pcp/api/Usuarios/<string:codigoUsuario>', methods=['DELETE'])
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

@app.route('/pcp/api/Usuarios/<string:codigo>', methods=['POST'])
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

@app.route('/pcp/api/Estrutura', methods=['POST'])
@token_required
def get_Estrutura():
    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    colecoes = data.get('colecoes')
    codEngenharias = data.get('codEngenharias', '0')
    codMP = data.get('codMP', '0')
    nomeComponente = data.get('nomeComponente', '0')
    TamanhoProduto = data.get('TamanhoProduto', '0')
    Excel = data.get('Excel', False)
    pagina = data.get('pagina', 0)  # Valor padrão: False, se 'estornar' não estiver presente no corpo
    itensPag = data.get('itensPag', 0)  # Valor padrão: False, se 'estornar' não estiver presente no corpo


    Endereco_det = Estrutura.Estrutura(colecoes, pagina, itensPag, codEngenharias, str(codMP), nomeComponente, Excel, TamanhoProduto)

    Endereco_det = pd.DataFrame(Endereco_det)

    # Obtém os nomes das colunas
    column_names = Endereco_det.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    end_data = []
    for _, row in Endereco_det.iterrows():
        end_dict = {column_name: row[column_name] for column_name in column_names}
        end_data.append(end_dict)

    return jsonify(end_data)


def Quebrar(item, item2):
    # Dividir a string em uma lista de elementos separados por vírgula
    elementos = item.split(", ")
    # Adicionar aspas simples em cada elemento da lista
    elementos_formatados = ["'" + elemento + "'" for elemento in elementos]
    # Juntar os elementos formatados em uma única string, separados por vírgula
    item2 = ", ".join(elementos_formatados)
    return item2


def DataFrame(item, item2):
    # Dividir a string em uma lista de elementos
    elementos = item.split(", ")

    # Criar um DataFrame com uma coluna chamada 'Elementos'
    df = pd.DataFrame({'Elementos': elementos})

    df.rename(
    columns = {'Elementos': item2},
    inplace = True)

    return df
@app.route('/pcp/api/Plano', methods=['GET'])
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
@app.route('/pcp/api/ColecoesPlano/<string:codigoplano>', methods=['GET'])
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
@app.route('/pcp/api/StatusPlano/<string:codigoPlano>', methods=['GET'])
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


@app.route('/pcp/api/Plano', methods=['PUT'])
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
@app.route('/pcp/api/Plano/<string:codigoPlano>', methods=['DELETE'])
@token_required
def delet_Plano(codigoPlano):
    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    dados = Usuarios.DeletarUsuarios(codigoPlano)
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

@app.route('/pcp/api/Plano/<string:codigo>', methods=['POST'])
@token_required
def update_Plano(codigo):

    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigo = str(codigo)
    descricao = data.get('descricao', '0')
    inicioVenda = data.get('inicioVenda', '0')
    finalVenda = data.get('finalVenda', '0')
    inicioFaturamento = data.get('inicioFaturamento', '0')
    finalFaturamento = data.get('finalFaturamento', '0')
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    codigo2 = Plano.ConsultarPlano(codigo)
    if codigo2 == 0:
        return jsonify({'message': f'Plano {codigo}  nao existe! ', 'Status': False})
    else:
        Plano.EditarPlano(codigo, descricao, inicioVenda, finalVenda, inicioFaturamento, finalFaturamento)
        return jsonify({'message': f'Plano {codigo}-{descricao} atualizado com sucesso', 'Status':True})

@app.route('/pcp/api/PesquisaColecoes', methods=['GET'])
@token_required
def get_Colecoes():
    # Obtém o código do usuário e a senha dos parâmetros da URL
    itensPag = request.args.get('itensPag',100)
    pagina = request.args.get('pagina',1)

    Endereco_det = ObterInfCSW.GetColecoes(pagina, itensPag)

    Endereco_det = pd.DataFrame(Endereco_det)

    # Obtém os nomes das colunas
    column_names = Endereco_det.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    end_data = []
    for _, row in Endereco_det.iterrows():
        end_dict = {column_name: row[column_name] for column_name in column_names}
        end_data.append(end_dict)

    return jsonify(end_data)
@app.route('/pcp/api/PesquisaTipoNotas', methods=['GET'])
@token_required
def get_PesquisaTipoNotass():
    # Obtém o código do usuário e a senha dos parâmetros da URL
    itensPag = request.args.get('itensPag',100)
    pagina = request.args.get('pagina',1)

    Endereco_det = ObterInfCSW.GetTipoNotas(pagina, itensPag)

    Endereco_det = pd.DataFrame(Endereco_det)

    # Obtém os nomes das colunas
    column_names = Endereco_det.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    end_data = []
    for _, row in Endereco_det.iterrows():
        end_dict = {column_name: row[column_name] for column_name in column_names}
        end_data.append(end_dict)

    return jsonify(end_data)

@app.route('/pcp/api/PesquisaLotes', methods=['GET'])
@token_required
def get_PesquisaLotes():
    # Obtém o código do usuário e a senha dos parâmetros da URL
    itensPag = request.args.get('itensPag',100)
    pagina = request.args.get('pagina',1)

    Endereco_det = ObterInfCSW.GetLotesCadastrados(pagina, itensPag)

    Endereco_det = pd.DataFrame(Endereco_det)

    # Obtém os nomes das colunas
    column_names = Endereco_det.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    end_data = []
    for _, row in Endereco_det.iterrows():
        end_dict = {column_name: row[column_name] for column_name in column_names}
        end_data.append(end_dict)

    return jsonify(end_data)

@app.route('/pcp/api/ColecaoPlano/<string:codigoplano>', methods=['PUT'])
@token_required
def criar_PlanoColecao(codigoplano):
    # Obtenha os dados do corpo da requisição
    novo_usuario = request.get_json()
    # Extraia os valores dos campos do novo usuário

    codcolecao = novo_usuario.get('codcolecao')
    nomecolecao = novo_usuario.get('nomecolecao')

    # inserir o novo usuário no banco de dados
    c = Plano.InserirColecaoNoPlano(codigoplano,codcolecao,nomecolecao)
    if c == 0:
        return jsonify({'message': f'Plano {codigoplano} ou {codcolecao} ja existem', 'status':False})
    else:

        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'message': f'Colecao {codcolecao} incluida no plano {codigoplano} com sucesso', 'status':True})

@app.route('/pcp/api/ColecaoPlano/<string:codigoPlano>', methods=['DELETE'])
@token_required
def delet_PlanoColecao(codigoPlano):
    novo_usuario = request.get_json()

    codigocolecao = novo_usuario.get('codigocolecao')

    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    dados = Plano.DeletarPlanoColecao(codigoPlano, codigocolecao)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)

