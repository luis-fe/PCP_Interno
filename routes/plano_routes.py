from flask import Blueprint, jsonify, request
from functools import wraps
from models import Plano, CalendarioProducao

plano_routes = Blueprint('plano_routes', __name__)
def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function

#Obter todos os Planos
@plano_routes.route('/pcp/api/Plano', methods=['GET'])
@token_required
def get_Plano():
    plano = Plano.ObeterPlanos()

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
        return jsonify({'00 Mensagem': f'Plano {codigoPlano}-{descricaoAnt} ja existe', '001 status':True,'01- Codigo Plano':codigoPlano
                       , '02- Descricao do Plano':descricaoAnt, '03- Inicio Venda':iniVendaAnt,
                        '04- Final Venda':finalVendaAnt,'05- Inicio Faturamento':inicioFatAnt,'06- Final Faturamento':finalFatAnt}), 201
    else:
        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'00 Mensagem': f'Plano {codigoPlano} nao existe', '001 status':False}), 201

@plano_routes.route('/pcp/api/Plano', methods=['POST'])
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
        return jsonify({'Mensagem': f'Plano {codigo}-{descricao} ja existe', 'status':False}), 201
    else:
        Plano.InserirPlano(codigo, descricao, inicoVenda, finalVenda, inicioFat, finalFat, usuario, dataGeracao)
        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'Mensagem': f'Plano {codigo}-{descricao} criado com sucesso', 'status':True}), 201
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


# API FEIA PARA REALIZAR UM UPDATE NAS INFORMACOES DO PLANO
@plano_routes.route('/pcp/api/Plano/<string:codigo>', methods=['PUT'])
@token_required
def update_Plano(codigo):

    # Etapa 1: Obtém os dados do corpo da requisição (JSON)
    #########################################################################################################
    data = request.get_json()
    codigo = str(codigo) #o codigo do plano a ser editado vai ser informado na url
    descricao = data.get('descricao', '0') # CASO NAO INFORMADO RETORNA PADRAO '0'
    inicioVenda = data.get('inicioVenda', '0')# CASO NAO INFORMADO RETORNA PADRAO '0'
    finalVenda = data.get('finalVenda', '0')# CASO NAO INFORMADO RETORNA PADRAO '0'
    inicioFaturamento = data.get('inicioFaturamento', '0')# CASO NAO INFORMADO RETORNA PADRAO '0'
    finalFaturamento = data.get('finalFaturamento', '0')# CASO NAO INFORMADO RETORNA PADRAO '0'
    ###########################################################################################################

    # Etapa 2: Verifica se o plano existe
    ###########################################################################################################
    consultaV1, consultaV2,consultaV3,consultaV4,consultaV5 ,consultaV6  = Plano.ConsultarPlano(codigo)
    if consultaV1 == 0: # 2.1 Caso o Plano nao exista retorna no JSON a resposta:
        return jsonify({'Mensagem': f'Plano {codigo}  nao existe! ', 'Status': False})

    else: # 2.2 Caso o Plano exista
        avaliar = CalendarioProducao.Avaliar_ExisteFeriadoPadrao(codigo) #2.21 Avaliando se existe tabela de feriado
        if avaliar == True:
            Plano.EditarPlano(codigo, descricao, inicioVenda, finalVenda, inicioFaturamento, finalFaturamento)
            CalendarioProducao.InserirPadrao_FeriadosPlano(codigo)
            return jsonify({'Mensagem': f'Plano {codigo}-{descricao} atualizado com sucesso', 'Status':True})

        else:
            print('segue o baile')
            Plano.EditarPlano(codigo, descricao, inicioVenda, finalVenda, inicioFaturamento, finalFaturamento)
            return jsonify({'Mensagem': f'Plano {codigo}-{descricao} atualizado com sucesso', 'Status':True})
@plano_routes.route('/pcp/api/ColecaoPlano/<string:codigoplano>', methods=['POST'])
@token_required
def criar_PlanoColecao(codigoplano):
    # Obtenha os dados do corpo da requisição
    novo_usuario = request.get_json()
    # Extraia os valores dos campos do novo usuário

    codcolecao = novo_usuario.get('codcolecao')
    nomecolecao = novo_usuario.get('nomecolecao')

    # inserir o novo usuário no banco de dados
    c = Plano.InserirColecaoNoPlano(codigoplano, codcolecao, nomecolecao)
    if c == 0:
        return jsonify({'message': f'Plano {codigoplano} ou {codcolecao} ja existem', 'status':False})
    else:

        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'message': f'Colecao {codcolecao} incluida no plano {codigoplano} com sucesso', 'status':True})

@plano_routes.route('/pcp/api/TipoNotaPlano/<string:codigoplano>', methods=['PUT'])
@token_required
def criar_PlanoTipoNota(codigoplano):
    # Obtenha os dados do corpo da requisição
    novo_usuario = request.get_json()
    # Extraia os valores dos campos do novo usuário

    tipoNota = novo_usuario.get('tipoNota')
    nome = novo_usuario.get('nome')

    # inserir o novo usuário no banco de dados
    c = Plano.InserirNotaNoPlano(codigoplano, tipoNota, nome)
    if c == 0:
        return jsonify({'message': f'Plano {codigoplano} ou {tipoNota} ja existem', 'status':False})
    else:

        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'message': f'Tipo nota  {tipoNota} incluida no plano {codigoplano} com sucesso', 'status':True})

@plano_routes.route('/pcp/api/LotePlano/<string:codigoplano>', methods=['PUT'])
@token_required
def criar_PlanoLote(codigoplano):
    # Obtenha os dados do corpo da requisição
    novo_usuario = request.get_json()
    # Extraia os valores dos campos do novo usuário

    lote = novo_usuario.get('lote')
    nome = novo_usuario.get('nome')

    # inserir o novo usuário no banco de dados
    c = Plano.InserirLoteNoPlano(codigoplano, lote, nome)
    if c == 0:
        return jsonify({'message': f'Plano {codigoplano} ou {lote} ja existem', 'status':False})
    else:

        # Retorne uma resposta indicando o sucesso da operação
        return jsonify({'message': f'Lote  {lote} incluida no plano {codigoplano} com sucesso', 'status':True})
@plano_routes.route('/pcp/api/ColecaoPlano/<string:codigoPlano>', methods=['DELETE'])
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

@plano_routes.route('/pcp/api/TipoNotaPlano/<string:codigoPlano>', methods=['DELETE'])
@token_required
def delet_PlanoNota(codigoPlano):
    novo_usuario = request.get_json()

    tipoNota = novo_usuario.get('tipoNota')

    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    dados = Plano.DeletarPlanoNota(codigoPlano, tipoNota)
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

@plano_routes.route('/pcp/api/LotePlano/<string:codigoPlano>', methods=['DELETE'])
@token_required
def delet_Lote(codigoPlano):
    novo_usuario = request.get_json()

    lote = novo_usuario.get('lote')

    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    dados = Plano.DeletarPlanoLote(codigoPlano, lote)
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
