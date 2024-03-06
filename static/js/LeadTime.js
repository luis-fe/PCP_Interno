//-------------------------------------------------------APIS--------------------------------------------------------------------------//
const ApiConsulta = 'http://192.168.0.183:8000/pcp/api/CargaOPs';
const ApiJustificativa = 'http://192.168.0.183:8000/pcp/api/CadastrarJustificativa';
const Token = 'a44pcp22';

const BotaoFiltro = document.getElementById('BotaoFiltros');
const ModalFiltros = document.getElementById('ModalFiltros');
const FecharModal = document.getElementById('Fechar');
const InputContem = document.getElementById('InputContem');
const InputNaoContem = document.getElementById('InputNaoContem');
const ConfirmarFiltro = document.getElementById('ConfirmarFiltro');
const BotaoExcel = document.getElementById('BotaoExcel');
const LabelOpsNormais = document.getElementById('LabelOpsNormais');
const LabelQtd = document.getElementById('LabelQtd');
const LabelOpsAtencao = document.getElementById('LabelOpsAtencao');
const LabelOpsAtrasadas = document.getElementById('LabelOpsAtrasadas');
const LabelOps = document.getElementById('LabelOps');
const container = document.getElementById('botaoContainer');
const LabelOp = document.getElementById('NumeroOP');
const ModalObs = document.getElementById('ModalJustificativa');
const InputObs = document.getElementById('InputJustificativa');
const FecharJustificativa = document.getElementById('FecharJustificativa');
const SalvarObs = document.getElementById('SalvarObs');
const modalLoading = document.getElementById("ModalLoading");
const ModalPendencia = document.getElementById("ModalPendencia");
const DivPendencias = document.getElementById("DivPendencias");
let VarOp = '';
let VarFase = '';
let VarObs = '';
container.style.justifyContent = 'center';

BotaoFiltro.addEventListener('click', () => {
    var rect = BotaoFiltro.getBoundingClientRect();
    ModalFiltros.style.top = rect.bottom + 'px';
    ModalFiltros.style.left = rect.left + 'px';
    ModalFiltros.style.display = 'block';
});

FecharModal.addEventListener('click', () => {
    ModalFiltros.style.display = 'none';
});

FecharJustificativa.addEventListener('click', () => {
    ModalObs.style.display = 'none';
});

function atualizarJustificativaBotao(op, fase, justificativa) {
    const botao = document.querySelector(`button[data-op="${op}"][data-fase="${fase}"]`);
    if (botao) {
        const justificativaElement = botao.querySelector('.Justificativa');
        if (justificativaElement) {
            justificativaElement.textContent = `Justificativa: ${justificativa}`;
        }
    }
}

async function OpGetObs(Op, Fase) {

    try {
        const response = await fetch(`http://192.168.0.183:8000/pcp/api/ConsultarJustificativa?ordemProd=${Op}&fase=${Fase}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': Token
            },
        });

        if (response.ok) {
            const data = await response.json();
            VarObs = data[0]['justificativa'];

        } else {
            throw new Error('Erro No Retorno');

        }
    } catch (error) {
        console.error(error);

    }
}

async function ConsultaOp(Api, Empresa, Filtro, Classificacao) {
    modalLoading.style.display = 'block'
    const Dados = {
        "empresa": Empresa,
        "filtro": Filtro,
        "classificar": Classificacao
    };

    try {
        const response = await fetch(`${Api}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': Token
            },
            body: JSON.stringify(Dados),
        });

        if (response.ok) {
            modalLoading.style.display = 'none'
            const data = await response.json();
            const DetalhamentoApi = data[0]['3 -Detalhamento'];
            container.innerHTML = '';
            LabelOps.innerHTML = `Qtd. Op's Abertas: <br> ${parseFloat(data[0]['1-Total OP']).toLocaleString('pt-BR')}`;
            LabelOpsNormais.innerHTML = `Qtd. Op's no Prazo: <br> ${parseInt(data[0]['1-Total OP']) - parseInt(data[0]['2- OPs Atrasadas']) - parseInt(data[0]['2.1- OPs Atencao'])} Ops`;
            LabelOpsAtencao.innerHTML = `Qtd. Op's em Atenção: <br> ${data[0]['2.1- OPs Atencao']}`;
            LabelOpsAtrasadas.innerHTML = `Qtd. Op's Atrasadas: <br> ${data[0]['2- OPs Atrasadas']}`;
            LabelQtd.innerHTML = `Qtd. Peças: <br> ${parseFloat(data[0]['0-Total DE pçs']).toLocaleString('pt-BR')}`;


            await DetalhamentoApi.forEach(dado => {
                const botao = document.createElement('button');

                botao.classList.add('botao');
                botao.setAttribute('data-op', dado.numeroOP);
                botao.setAttribute('data-fase', dado.codFase);

                if (dado.prioridade === '1-URGENTE') {
                    const urgenteSymbol = document.createElement('span');
                    urgenteSymbol.innerHTML = '🚨'; // Símbolo de ponto de exclamação
                    urgenteSymbol.style.backgroundColor = 'black';
                    urgenteSymbol.style.fontSize = '30px';
                    botao.appendChild(urgenteSymbol);
                }

                const conteudoBotao = document.createElement('strong');

                conteudoBotao.innerHTML = `
                <span class="CodFase">Fase: ${dado.codFase} - ${dado.nomeFase}</span><br>
                <span class="NumeroOp">OP:${dado.numeroOP} / Qtd: ${dado['Qtd Pcs']} Pçs</span><br>
                <span class="NumeroOp">Engenharia: ${dado.codProduto}</span><br>
                <span class="Engenharias">${dado.descricao}</span><br>
                <span class="Engenharias">Tipo Op: ${dado.codTipoOP}</span><br>
                <span class="Engenharias">Responsável: ${dado.responsavel}<br>
                <span class="Engenharias">Meta: ${dado.meta} dias<br>
                <span class="Engenharias">Dias na Fase: ${dado['dias na Fase']}<br>
                <span class="Justificativa">Justificativa: ${dado.justificativa}</span>
                <span style="${dado['Status Aguardando Partes'] === 'PENDENTE' || dado['Status Aguardando Partes'] === 'OK' ? ' font-size: 50px; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center;' : ''}">
                    ${dado['Status Aguardando Partes'] === 'PENDENTE' ? '⚠️' : ''}
                    ${dado['Status Aguardando Partes'] === 'OK' ? '✅' : ''}
                </span>
            `;
            botao.onmouseover = () => {
                if (dado['Status Aguardando Partes'] === 'PENDENTE') {
                    mostrarModalPendente(botao, dado);
                }
            };

            botao.onmouseout = () => {
                fecharModalPendente();
            };

                botao.appendChild(conteudoBotao);

                switch (dado.status) {
                    case '2-Atrasado':
                        botao.style.backgroundColor = 'red';
                        break;
                    case '1-Atencao':
                        botao.style.backgroundColor = 'yellow';
                        botao.style.color = 'black';
                        break;
                    case '0-Normal':
                        botao.style.backgroundColor = '#3498db';
                        break;
                    // Adicione outros casos conforme necessário
                }


                botao.addEventListener('click', async () => {
                    await OpGetObs(dado.numeroOP, dado.codFase);
                    LabelOp.innerHTML = `OP: ${dado.numeroOP}`;
                    InputObs.value = `${VarObs}`;
                    InputObs.focus();

                    // Calcular a posição considerando a barra de rolagem
                    var rect = botao.getBoundingClientRect();
                    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;

                    ModalObs.style.top = rect.bottom + scrollTop + 'px';
                    ModalObs.style.left = rect.left + 'px';
                    ModalObs.style.display = 'block';

                    VarOp = dado.numeroOP;
                    VarFase = dado.codFase;
                });
                container.appendChild(botao);

                function mostrarModalPendente(botao, dado) {
                    var rect = botao.getBoundingClientRect();
                    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                    const Pendencia = dado.estaPendente
                    ModalPendencia.style.top = rect.bottom + scrollTop + 'px';
                    ModalPendencia.style.left = rect.left + 'px';
                    ModalPendencia.style.display = 'block';

                    Pendencia.forEach(Pendencia => {
                        const label = document.createElement('label');
                        label.textContent = Pendencia;
                        label.style.fontSize = '22px'
                        DivPendencias.appendChild(label);
                    })
                }
                
                function fecharModalPendente() {
                    // Oculta o modal
                    ModalPendencia.style.display = 'none';
                
                    // Limpa o conteúdo dentro de DivPendencias
                    DivPendencias.innerHTML = '';
                }
            });

        } else {
            modalLoading.style.display = 'none'
            throw new Error('Erro No Retorno');
        }
    } catch (error) {
        modalLoading.style.display = 'none'
        console.error(error);
    }
}



SalvarObs.addEventListener('click', async () => {
    dadoApi = {
        "ordemProd": VarOp,
        "fase": VarFase,
        "justificativa": InputObs.value
    };

    await fetch(ApiJustificativa, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': Token
        },
        body: JSON.stringify(dadoApi),
    })
        .then(response => {
            if (response.ok) {
                alert('Justificativa salva com Sucesso');
                InputObs.value = ''; // Limpar o conteúdo do InputObs
                ModalObs.style.display = 'none'; // Certifique-se de que ModalObs está acessível
                atualizarJustificativaBotao(VarOp, VarFase, dadoApi.justificativa);
                return response.json();
            } else {
                throw new Error('Não foi possível Salvar a Justificativa');
            }
        })
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            console.error(error);
        });
});


async function ExportarExcel(Api, Empresa, Filtro) {
    const Dados = {
        "empresa": Empresa,
        "filtro": Filtro
    };

    try {
        const response = await fetch(`${Api}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': Token
            },
            body: JSON.stringify(Dados),
        });

        if (response.ok) {
            const data = await response.json();
            const DetalhamentoApi = data[0]['3 -Detalhamento'];
            const nomeArquivo = 'Dados Ops.xlsx';
            const wb = XLSX.utils.book_new();
            const ws = XLSX.utils.json_to_sheet(DetalhamentoApi);

            // Adicionar a planilha ao workbook
            XLSX.utils.book_append_sheet(wb, ws, "Dados Op's");

            // Salvar o arquivo
            XLSX.writeFile(wb, nomeArquivo);

        } else {
            throw new Error('Erro No Retorno');
        }
    } catch (error) {
        console.error(error);
    }
}

BotaoExcel.addEventListener('click', () => {
    ExportarExcel(ApiConsulta, '1', InputContem.value);
});

ConfirmarFiltro.addEventListener('click', () => {
    ConsultaOp(ApiConsulta, '1', InputContem.value, valorSelecionado).catch(error => {
        console.error('Erro ao consultar OP:', error);
    });
    console.log(InputContem.value);
});

window.addEventListener('load', () => {
    ConsultaOp(ApiConsulta, '1', '', '');
});

var valorSelecionado = document.getElementById("btnLeadTime").getAttribute("data-valor");


document.getElementById("btnLeadTime").classList.add("botao-selecionado");

// Função para selecionar o botão e deselecionar o outro
function selecionarBotao(botaoClicado) {
    var btnUrgente = document.getElementById("btnUrgente");
    var btnLeadTime = document.getElementById("btnLeadTime");

    if (botaoClicado === btnUrgente) {
        btnUrgente.classList.add("botao-selecionado");
        btnLeadTime.classList.remove("botao-selecionado");
        valorSelecionado = botaoClicado.getAttribute("data-valor");
    } else {
        btnUrgente.classList.remove("botao-selecionado");
        btnLeadTime.classList.add("botao-selecionado");
        valorSelecionado = botaoClicado.getAttribute("data-valor");
    }
}

function atualizarPagina() {
    
    const filtro = InputContem.value;
    const classificacaoSalva = valorSelecionado;


    ConsultaOp(ApiConsulta, '1', filtro, classificacaoSalva).catch(error => {
        console.error('Erro ao consultar OP:', error);
    });

}

// Chama a função de atualização a cada 15 minutos (em milissegundos)
const intervaloDeAtualizacao = 15 * 60 * 1000; // 15 minutos
setInterval(atualizarPagina, intervaloDeAtualizacao);
