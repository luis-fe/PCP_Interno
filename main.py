from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import pandas as pd
import os
from routes import routes_blueprint
from functools import wraps
from models import ABC_PLANO, CalendarioProducao, AutomacaoSugestaoPedidos, ObterInfCSW, Vendas
from werkzeug.utils import secure_filename

app = Flask(__name__)
port = int(os.environ.get('PORT', 8000))


app.register_blueprint(routes_blueprint)
#Aqui registo todas as rotas , url's DO PROJETO, para acessar bastar ir na pasta "routes",
#duvidas o contato (62)99351-42-49 ou acessar a documentacao do projeto em:


CORS(app)
def token_required(f): #Aqui passamos o token fixo, que pode ser alterado
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token == 'a44pcp22':  # Verifica se o token é igual ao token fixo
            return f(*args, **kwargs)
        return jsonify({'message': 'Acesso negado'}), 401

    return decorated_function



# Defina o diretório onde as imagens serão armazenadas
UPLOAD_FOLDER = 'imagens'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rota para enviar a imagem
@app.route('/pcp/api/upload/<string:idchamado>', methods=['POST'])
def upload_image(idchamado):
    # Verifique se a solicitação possui um arquivo anexado
    if 'file' not in request.files:
        return jsonify({'message': 'chamado sem anexo'}), 200

    file = request.files['file']

    # Verifique se o nome do arquivo é vazio
    if file.filename == '':
        return jsonify({'message': 'chamado sem anexo'}), 200

    # Verifique se a extensão do arquivo é permitida (opcional)
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if not file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
        return jsonify({'message': 'Extensão de arquivo não permitida'}), 400

    # Renomeie o arquivo com o ID do chamado e a extensão original
    filename = secure_filename(f'{idchamado}.{file.filename.rsplit(".", 1)[1]}')

    # Salve o arquivo na pasta de uploads usando idchamado como diretório
    upload_directory = os.path.join(app.config['UPLOAD_FOLDER'], idchamado)

    # Verifique se o diretório existe e crie-o se não existir
    os.makedirs(upload_directory, exist_ok=True)

    # Salve o arquivo com o novo nome
    file.save(os.path.join(upload_directory, filename))

    return jsonify({'message': 'Arquivo enviado com sucesso'}), 201

@app.route('/pcp/api/get_image/<string:idchamado>', methods=['GET'])
def get_image(idchamado):
    filename = idchamado
    return send_from_directory(f'imagens/{idchamado}', filename)


@app.route('/pcp/api/PesquisaColecoes', methods=['GET'])
@token_required
def get_Colecoes():
    # Obtém o código do usuário e a senha dos parâmetros da URL
    itensPag = request.args.get('itensPag',1000)
    pagina = request.args.get('pagina',1)
    client_ip = request.remote_addr

    Endereco_det = ObterInfCSW.GetColecoes(pagina, itensPag, client_ip)

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
    client_ip = request.remote_addr


    Endereco_det = ObterInfCSW.GetTipoNotas(pagina, itensPag, client_ip)

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
    client_ip = request.remote_addr


    Endereco_det = ObterInfCSW.GetLotesCadastrados(pagina, itensPag, client_ip)

    Endereco_det = pd.DataFrame(Endereco_det)

    # Obtém os nomes das colunas
    column_names = Endereco_det.columns
    # Monta o dicionário com os cabeçalhos das colunas e os valores correspondentes
    end_data = []
    for _, row in Endereco_det.iterrows():
        end_dict = {column_name: row[column_name] for column_name in column_names}
        end_data.append(end_dict)

    return jsonify(end_data)





@app.route('/pcp/api/Vendas/<string:codigoPlano>', methods=['GET'])
@token_required
def get_VendasPlano(codigoPlano):
    plano = Vendas.VendasporSku(codigoPlano)
    plano = pd.DataFrame(plano)

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

@app.route('/pcp/api/AtualizarAutomacao', methods=['GET'])
def get_AtualizarAutomacao():
    client_ip = request.remote_addr

    usuarios = AutomacaoSugestaoPedidos.AplicandoAtualizacao(client_ip)
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


@app.route('/pcp/api/RankingABCVendas', methods=['POST'])
@token_required
def vendas():
    data = request.get_json()
    codigoPlano = data.get('plano')
    excel = data.get('excel', False)
    aprovado = data.get('aprovado', True)
    engenharia = data.get('engenharia', '0')
    descricao = data.get('descricao', '0')
    categoria = data.get('categoria', '0')
    MARCA = data.get('MARCA', '0')
    pagina = data.get('pagina', 0)  # Valor padrão: False, se 'estornar' não estiver presente no corpo
    itensPag = data.get('itensPag', 1)  # Valor padrão: False, se 'estornar' não estiver presente no corpo
    detalhaengenharias =  data.get('detalhaengenharias','0')
    client_ip = request.remote_addr


    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    if detalhaengenharias == '0':
        dados, nome = Vendas.VendasporSku(client_ip, codigoPlano, aprovado, excel, pagina, itensPag, engenharia, descricao, categoria, MARCA)
        dados = pd.DataFrame(dados)

    else:
        dados1, nome = Vendas.VendasporSku(client_ip, codigoPlano, aprovado, excel, pagina, itensPag, engenharia, descricao, categoria, MARCA)
        dados = Vendas.Detalha_EngenhariaABC(detalhaengenharias, nome)
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

@app.route('/pcp/api/EditarABCPlano', methods=['POST'])
@token_required
def EditarABCPlano():
    data = request.get_json()
    codigoPlano = data.get('plano')
    a_ = data.get('a', '0')
    b_ = data.get('b', '0')
    c_ = data.get('c', '0')
    c1_ = data.get('c1', '0')
    c2_ = data.get('c2', '0')
    c3_ = data.get('c3', '0')

    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    dados = ABC_PLANO.Editar(a_, b_, c_, c1_, c2_, c3_, codigoPlano)
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

@app.route('/pcp/api/ABCPlano/<string:Plano>', methods=['GET'])
def get_ABCPlano(Plano):
    usuarios = ABC_PLANO.getABCPlano(Plano)
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

@app.route('/pcp/api/PlanoFeriado/<string:Plano>', methods=['GET'])
def get_PlanoFeriado(Plano):
    usuarios = CalendarioProducao.Get_feriados(Plano)
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

