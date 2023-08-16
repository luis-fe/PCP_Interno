from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
from routes import routes_blueprint
from functools import wraps
from models import ABC_PLANO, CalendarioProducao, Estrutura, AutomacaoSugestaoPedidos, ObterInfCSW, Vendas

app = Flask(__name__)
port = int(os.environ.get('PORT', 8000))
app.register_blueprint(routes_blueprint)

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
@app.route('/TelaEstrutura')
def telaEstrutura():
    return render_template('TelaEstrutura.html')
@app.route('/TelaPlano')
def TelaPlano():
    return render_template('TelaPlano.html')
@app.route('/TelaPrincipal')
def TelaPrincipal():
    return render_template('TelaPrincipal.html')
@app.route('/TelaUsuarios')
def TelaUsuarios():
    return render_template('TelaUsuarios.html')




@app.route('/pcp/api/Estrutura', methods=['POST'])
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
    itensPag = data.get('itensPag', 0)  # Valor padrão: False, se 'estornar' não estiver presente no corpo
    detalhaengenharias =  data.get('detalhaengenharias','0')
    client_ip = request.remote_addr


    # Obtém os dados do corpo da requisição (JSON)
    data = request.get_json()
    codigoPlano = str(codigoPlano)
    # Verifica se a coluna "funcao" está presente nos dados recebidos
    if detalhaengenharias == '0':
        dados, nome = Vendas.VendasporSku(client_ip, codigoPlano, aprovado, excel, pagina, itensPag, engenharia, descricao, categoria, MARCA)
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

