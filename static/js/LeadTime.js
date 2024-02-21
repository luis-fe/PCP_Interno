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

async function ConsultaOp(Api, Empresa, Filtro) {
    modalLoading.style.display = 'block'
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
            modalLoading.style.display = 'none'
            const data = await response.json();
            console.log(data);
            const DetalhamentoApi = data[0]['3 -Detalhamento'];
            container.innerHTML = '';
            LabelOps.innerHTML = `Qtd. Op's Abertas: <br> ${parseFloat(data[0]['1-Total OP']).toLocaleString('pt-BR')}`;
            LabelOpsNormais.innerHTML = `Qtd. Op's Normais: <br> ${parseInt(data[0]['1-Total OP']) - parseInt(data[0]['2- OPs Atrasadas']) - parseInt(data[0]['2.1- OPs Atencao'])} Ops`;
            LabelOpsAtencao.innerHTML = `Qtd. Op's em Atenção: <br> ${data[0]['2.1- OPs Atencao']}`;
            LabelOpsAtrasadas.innerHTML = `Qtd. Op's Atrasadas: <br> ${data[0]['2- OPs Atrasadas']}`;

            await DetalhamentoApi.forEach(dado => {
                const botao = document.createElement('button');
            
                botao.classList.add('botao');
                botao.setAttribute('data-op', dado.numeroOP);
                botao.setAttribute('data-fase', dado.codFase);
            
                botao.innerHTML = `
                    <strong><span class="CodFase">Fase: ${dado.codFase} - ${dado.nomeFase}</span><br>
                    <span class="NumeroOp">OP:${dado.numeroOP} / Qtd: ${dado['Qtd Pcs']} Pçs</strong></span><br>
                    <span class="Engenharias">Tipo Op: ${dado.codTipoOP}</strong></span><br>
                    <span class="Engenharias">${dado.descricao}</strong></span><br>
                    Responsável: ${dado.responsavel}<br>
                    Meta: ${dado.meta} dias<br>
                    Dias na Fase: ${dado['dias na Fase']}<br>
                    <span class="Justificativa">Justificativa: ${dado.justificativa}</span>
                `;
                
                
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
                    console.log(dado);
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
    ConsultaOp(ApiConsulta, '1', InputContem.value).catch(error => {
        console.error('Erro ao consultar OP:', error);
    });
    console.log(InputContem.value);
});

window.addEventListener('load', () => {
    ConsultaOp(ApiConsulta, '1', '');
});
