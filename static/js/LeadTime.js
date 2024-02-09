//-------------------------------------------------------APIS--------------------------------------------------------------------------//
const ApiConsulta = 'http://192.168.0.183:8000/pcp/api/CargaOPs';
const Token =  'a44pcp22'

const BotaoFiltro = document.getElementById('BotaoFiltros');
const ModalFiltros = document.getElementById('ModalFiltros');
const FecharModal = document.getElementById('Fechar');
const InputContem = document.getElementById('InputContem');
const InputNaoContem = document.getElementById('InputNaoContem');
const ConfirmarFiltro = document.getElementById('ConfirmarFiltro');
const BotaoExcel = document.getElementById('BotaoExcel');
const LabelOpsNormais = document.getElementById('LabelOpsNormais');
const LabelOpsAtrasadas = document.getElementById('LabelOpsAtrasadas');
const LabelOps = document.getElementById('LabelOps');
const container = document.getElementById('botaoContainer');
container.style.justifyContent = 'center'

BotaoFiltro.addEventListener('click', () => {
    var rect = BotaoFiltro.getBoundingClientRect();
    ModalFiltros.style.top = rect.bottom + 'px';
    ModalFiltros.style.left = rect.left + 'px';
    ModalFiltros.style.display = 'block';
});

FecharModal.addEventListener('click', () => {
    ModalFiltros.style.display = 'none'
});


async function ConsultaOp(Api, Empresa, Filtro) {
    const Dados = {
        "empresa": Empresa,
        "filtro": Filtro

    }
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
            console.log(data);
            const DetalhamentoApi = data[0]['3 -Detalhamento'];
            container.innerHTML = '';
            LabelOps.innerHTML = `Qtd. Op's Abertas: <br> ${parseFloat(data[0]['1-Total OP']).toLocaleString('pt-BR')}`;
            LabelOpsNormais.innerHTML = `Qtd. Op's Normais: <br> ${parseInt(data[0]['1-Total OP']) - parseInt(data[0]['2- OPs Atrasadas'])} Ops`;
            LabelOpsAtrasadas.innerHTML = `Qtd. Op's Atrasadas: <br> ${data[0]['2- OPs Atrasadas']}`
             await DetalhamentoApi.forEach(dado => {
                const botao = document.createElement('button');
                
                botao.classList.add('botao');
                botao.innerHTML = `
                
                <strong><span class="CodFase">Fase: ${dado.codFase} - ${dado.nomeFase}</span><br>
                <span class="NumeroOp">OP:${dado.numeroOP} / Qtd: ${dado['Qtd Pcs']} Pçs</strong></span><br>
                <span class="Engenharias">${dado.descricao}</strong></span><br>
                Responsável: ${dado.responsavel}<br>
                Meta: ${dado.meta} dias<br>
                Dias na Fase: ${dado['dias na Fase']}<br>
                <span class="Justificativa">Justificativa: ${dado.justificativa}</span>
            `;
            if (dado.status === '⚠️atrasado') {
                botao.style.backgroundColor = 'red';
            }
                botao.addEventListener('click', () => {
                    // Aqui você pode adicionar a lógica que deseja quando um botão é clicado
                    console.log(dado); // Por exemplo, imprimir os detalhes do dado
                });
                container.appendChild(botao);
            });
        } else {
            throw new Error('Erro No Retorno');
        }
    } catch (error) {
        console.error(error);
    }
}

async function ExportarExcel(Api, Empresa, Filtro) {
    const Dados = {
        "empresa": Empresa,
        "filtro": Filtro

    }
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

BotaoExcel.addEventListener('click', () =>{
    ExportarExcel(ApiConsulta, '1', InputContem.value)
})

ConfirmarFiltro.addEventListener('click', () =>{
    ConsultaOp(ApiConsulta, '1', InputContem.value);
    console.log(InputContem.value);
})


window.addEventListener('Load', ConsultaOp(ApiConsulta, '1', ''));
