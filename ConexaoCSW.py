import jaydebeapi
import pytz
import datetime
import ConexaoPostgreMPL
def obterHoraAtual():
    fuso_horario = pytz.timezone('America/Sao_Paulo')  # Define o fuso horário do Brasil
    agora = datetime.datetime.now(fuso_horario)
    hora_str = agora.strftime('%Y-%m-%d %H:%M:%S')
    return hora_str

def Conexao():
    conn = jaydebeapi.connect(
    'com.intersys.jdbc.CacheDriver',
    'jdbc:Cache://192.168.0.25:1972/CONSISTEMs',
    {'user': 'root', 'password': 'ccscache'},
    'CacheDB.jar'
)
    return conn


def ControleRequisicao(nome, tempoexecucao,client_ip):
    conn = ConexaoPostgreMPL.conexao()
    datahora = obterHoraAtual()
    insert = 'Insert into pcp."ControleRequisicaoCSW" ' \
             '(requisicao, data, tempoexecucao, client_ip) values (%s , %s, %s, %s)'
    cursor = conn.cursor()
    cursor.execute(insert, (nome, datahora,tempoexecucao,client_ip,))
    conn.commit()
    cursor.close()