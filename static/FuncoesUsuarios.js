function Usuarios() {
    const username = document.getElementById('InputLogin').value;
    const password = document.getElementById('InputSenha').value;
    const apiUrl = `http://192.168.0.183:8000/pcp/api/UsuarioSenha?codigo=${username}&senha=${password}`;
    const UsuarioInvalido = document.getElementById('UsuarioInválido')
  
    fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'a44pcp22'
      }
    })
    .then(function(response) {
      if (response.ok) {
        return response.json();
      } else {
        return response.json();
      }
    })
    .then(function(data) {
      // Verifica o valor do campo "status" na resposta da API
      if (data.status === true) {
        const nomeUsuario = data.Usuario;
        localStorage.setItem('nomeUsuario', nomeUsuario);
        window.location.href = "TelaPrincipal.html";
      } else {
        UsuarioInvalido.style.display = "block"
      }
    })
    .catch(function(error) {
      // Lidar com erros
      console.error(error);
    });
    
  }

  

 //------------------------------------------------------Código para Criação da Modal de Novo Usuário!-----------------------------------------------------//
  
  const BotaoCadUsuario = document.getElementById('BotaoCadUsuario');
  const modalNovo = document.getElementById('modalNovo');
  const fecharModal = document.getElementById('fecharModal');
  const InputNome = document.getElementById('InputUsuario');
  
//  Função para abrir a modal //
  BotaoCadUsuario.addEventListener('click', function() {
    modalNovo.style.display = 'block';
    InputNome.focus();
  });
  
  // Função para Fechar a Modal
  fecharModal.addEventListener('click', function() {
    modalNovo.style.display = 'none';
    document.getElementById('InputUsuario').value = '';
    document.getElementById('InputLogin').value = '';
    document.getElementById('InputSenha').value = '';
  });
  
    // Função para o foco da input ir para a Próxima Input dentro da Modal//
  function checkEnterModal(event, nextInputId) {
    if (event.key === "Enter") {
        event.preventDefault();
        document.getElementById(nextInputId).focus();
    }
  }

  // ------------------------------------------------------ FUNÇÃO PAR SALVAR OS USUÁRIOS-------------------------------------------------------------------------//
  
  
  function salvarUsuario() {
    const inputUsuario = document.getElementById('InputUsuario');
    const inputLogin = document.getElementById('InputLogin');
    const inputSenha = document.getElementById('InputSenha');
  
    if (inputUsuario.value === '' && inputLogin.value === '' && inputSenha.value === '') {
      inputUsuario.style.borderColor = 'red';
      inputUsuario.placeholder = 'Campo obrigatório';
      inputLogin.style.borderColor = 'red';
      inputLogin.placeholder = 'Campo obrigatório';
      inputSenha.style.borderColor = 'red';
      inputSenha.placeholder = 'Campo obrigatório';
      setTimeout(function() {
        inputUsuario.style.borderColor = 'lightgray';
        inputUsuario.placeholder = '';
        inputLogin.style.borderColor = 'lightgray';
        inputLogin.placeholder = '';
        inputSenha.style.borderColor = 'lightgray';
        inputSenha.placeholder = '';
      }, 5000);
      return;
    }
  
    if (inputUsuario.value === '' && inputLogin.value === '') {
      inputUsuario.style.borderColor = 'red';
      inputUsuario.placeholder = 'Campo obrigatório';
      inputLogin.style.borderColor = 'red';
      inputLogin.placeholder = 'Campo obrigatório';
      setTimeout(function() {
        inputUsuario.style.borderColor = 'lightgray';
        inputUsuario.placeholder = '';
        inputLogin.style.borderColor = 'lightgray';
        inputLogin.placeholder = '';
      }, 5000);
      return;
    }
  
    if (inputUsuario.value === '' && inputSenha.value === '') {
      inputUsuario.style.borderColor = 'red';
      inputUsuario.placeholder = 'Campo obrigatório';
      inputSenha.style.borderColor = 'red';
      inputSenha.placeholder = 'Campo obrigatório';
      setTimeout(function() {
        inputUsuario.style.borderColor = 'lightgray';
        inputUsuario.placeholder = '';
        inputSenha.style.borderColor = 'lightgray';
        inputSenha.placeholder = '';
      }, 5000);
      return;
    }
  
    if (inputLogin.value === '' && inputSenha.value === '') {
      inputLogin.style.borderColor = 'red';
      inputLogin.placeholder = 'Campo obrigatório';
      inputSenha.style.borderColor = 'red';
      inputSenha.placeholder = 'Campo obrigatório';
      setTimeout(function() {
        inputLogin.style.borderColor = 'lightgray';
        inputLogin.placeholder = '';
        inputSenha.style.borderColor = 'lightgray';
        inputSenha.placeholder = '';
      }, 5000);
      return;
    }
  
    if (inputUsuario.value === '') {
      inputUsuario.style.borderColor = 'red';
      inputUsuario.placeholder = 'Campo obrigatório';
      setTimeout(function() {
        inputUsuario.style.borderColor = 'lightgray';
        inputUsuario.placeholder = '';
  
      }, 5000);
      return;
    }
  
    if (inputLogin.value === '') {
      inputLogin.style.borderColor = 'red';
      inputLogin.placeholder = 'Campo obrigatório';
      setTimeout(function() {
        inputLogin.style.borderColor = 'lightgray';
        inputLogin.placeholder = '';
      }, 5000);
      return;
    }
  
    if (inputSenha.value === '') {
      inputSenha.style.borderColor = 'red';
      inputSenha.placeholder = 'Campo obrigatório';
      setTimeout(function() {
        inputSenha.style.borderColor = 'lightgray';
        inputSenha.placeholder = '';
      }, 5000);
      return;
    }
  
    const cadastroUsuario = {
      codigo: inputLogin.value,
      nome: inputUsuario.value,
      senha: inputSenha.value
    };
  
    const apiUrl = `http://192.168.0.183:8000/pcp/api/Usuarios`;
  
    fetch(apiUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'a44pcp22'
      },
      body: JSON.stringify(cadastroUsuario)
    })
      .then(function(response) {
        if (response.ok) {
          // Sucesso ao salvar o usuário
          return response.json();
        } else {
          // Erro ao salvar o usuário
          throw new Error('Erro ao salvar o usuário');
        }
      })
      .then(function(data) {
        console.log(data); // Exibe a resposta completa da API no console
        if (data.message.includes('criado com sucesso')) {
          // Usuário criado com sucesso
          alert(data.message);
          modalNovo.style.display = 'none';
          document.getElementById('InputUsuario').value = '';
          document.getElementById('InputLogin').value = '';
          document.getElementById('InputSenha').value = '';
        } else if (data.message.includes('ja existe')) {
          // Usuário já existe
          alert(data.message);
        } else {
          // Mensagem desconhecida
          throw new Error('Mensagem desconhecida retornada pela API');
        }
      })
      .catch(function(error) {
        // Erro na requisição ou tratamento dos resultados
        console.error(error);
        // Realizar alguma ação, como exibir uma mensagem de erro
      });
  }
  
// ----------------------------------------------Função para exibir a tabela de Usuários---------------------------------------------- //
const apiUrl = 'http://192.168.0.183:8000/pcp/api/Usuarios';
let indiceExibicao = 0;
let totalUsuarios = 0;
let totalPaginas = 0;
let paginaAtual = 0;





function criarTabelaUsuarios(listaUsuarios) {
  const tabela = document.getElementById('TabelaUsuarios');
  tabela.innerHTML = ''; // Limpa o conteúdo da tabela antes de preenchê-la novamente

  // Cria o cabeçalho da tabela
  const cabecalho = document.createElement('thead');
  const cabecalhoRow = document.createElement('tr');
  const colunaCheckbox = document.createElement('th');
  const colunaCodigo = document.createElement('th');
  const colunaNome = document.createElement('th');

  colunaCheckbox.textContent = '';
  colunaCodigo.textContent = 'Login';
  colunaNome.textContent = 'Nome Usuário';

  colunaCheckbox.style.width = '30px';
  colunaCodigo.style.width = '100px';
  colunaNome.style.width = '250px';

  cabecalhoRow.appendChild(colunaCheckbox);
  cabecalhoRow.appendChild(colunaCodigo);
  cabecalhoRow.appendChild(colunaNome);
  cabecalho.appendChild(cabecalhoRow);
  tabela.appendChild(cabecalho);

  // Preenche a tabela com os dados dos usuários
  const usuariosExibicao = listaUsuarios.slice(indiceExibicao, indiceExibicao + 15);

  usuariosExibicao.forEach(usuario => {
    const row = document.createElement('tr');
    const colunaCheckbox = document.createElement('td');
    const colunaCodigo = document.createElement('td');
    const colunaNome = document.createElement('td');
    const checkbox = document.createElement('input');
    checkbox.type = 'checkbox';
    checkbox.value = usuario.codigo;
    checkbox.name = 'checkboxUsuario';
    checkbox.addEventListener('change', function(event) {
      const checkboxes = document.getElementsByName('checkboxUsuario');
      checkboxes.forEach(box => {
        if (box !== event.target) {
          box.checked = false;
        }
      });
    });
    colunaCheckbox.appendChild(checkbox);
    colunaCodigo.textContent = usuario.codigo;
    colunaNome.textContent = usuario.nome;
    row.appendChild(colunaCheckbox);
    row.appendChild(colunaCodigo);
    row.appendChild(colunaNome);
    tabela.appendChild(row);
  });

  const botaoProximo = document.getElementById('ButtonProximaPagina');
  const botaoAnterior = document.getElementById('ButtonPaginaAnterior');
  const labelPagina = document.getElementById('LabelContagemPagina');

  if (indiceExibicao === 0) {
    botaoAnterior.disabled = true;
    labelPagina.textContent = `Página ${paginaAtual + 1} de ${totalPaginas}`;
  } else {
    botaoAnterior.disabled = false;
    labelPagina.textContent = `Página ${paginaAtual + 1} de ${totalPaginas}`;
  }

  if (usuariosExibicao.length < 15) {
    botaoProximo.disabled = true;
    labelPagina.textContent = `Página ${paginaAtual + 1} de ${totalPaginas}`;
  } else {
    botaoProximo.disabled = false;
    labelPagina.textContent = `Página ${paginaAtual + 1} de ${totalPaginas}`;
  }
}

const modalLoading1 = document.getElementById("ModalLoading1");

function AbrirModalLoading1() {
  modalLoading1.style.display = "block";
}

// Função para fechar a modal de carregamento
function FecharModalLoading1() {
  modalLoading1.style.display = "none";
  document.getElementById('ImagemLoading').value = '';
}

function carregarUsuarios() {
  AbrirModalLoading1();
  fetch(apiUrl, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'a44pcp22'
    },
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Erro ao obter a lista de usuários');
      }
    })
    .then(data => {
      totalUsuarios = data.length;
      totalPaginas = Math.ceil(totalUsuarios / 15);
      FecharModalLoading1();
      criarTabelaUsuarios(data);
    })
    .catch(error => {
      console.error(error);
      FecharModalLoading1();
    });
}

function carregarProximosUsuarios() {
  indiceExibicao += 15;

  // Verifica se o índice de exibição ultrapassa o número total de usuários
  if (indiceExibicao >= totalUsuarios) {
    indiceExibicao = Math.max(0, totalUsuarios - 15);
  }

  paginaAtual = Math.floor(indiceExibicao / 15);
  carregarUsuarios();
}

function carregarUsuariosAnteriores() {
  indiceExibicao -= 15;
  if (indiceExibicao < 0) {
    indiceExibicao = 0;
  }

  paginaAtual = Math.floor(indiceExibicao / 15);
  carregarUsuarios();
}

const botaoProximo = document.getElementById('ButtonProximaPagina');
const botaoAnterior = document.getElementById('ButtonPaginaAnterior');

botaoProximo.addEventListener('click', carregarProximosUsuarios);
botaoAnterior.addEventListener('click', carregarUsuariosAnteriores);

window.addEventListener('load', carregarUsuarios);

// -----------------------------------------------------------------Código para Editar o Usuário ----------------------------------------------------------------------//
const BotaoEditar = document.getElementById('ButtonEditar');
const ModalEditar = document.getElementById('ModalEditar');
const FecharModalEditar = document.getElementById('FecharModalEditar');
const checkboxes = document.getElementsByName('checkboxUsuario');

BotaoEditar.addEventListener('click', function() {
  const checkboxSelecionada = Array.from(checkboxes).find(checkbox => checkbox.checked);
  if (!checkboxSelecionada) {
    alert("Selecione um Usuário!");
    return;
  }

  const linhaSelecionada = checkboxSelecionada.closest('tr');
  const colunas = linhaSelecionada.getElementsByTagName('td');
  const codigo = colunas[1].textContent.toString();
  const Nome = colunas[2].textContent;
  const FocuInputUsuario = document.getElementById('InputUsuarioEditar');

  let SenhaUsuario;

  function ObterSenha() {
    const Usuers = {
      "codigo": codigo
    }

    const apiUrl = 'http://192.168.0.183:8000/pcp/api/UsuarioSenha';
    fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'a44pcp22'
      },
      body: JSON.stringify(Usuers),
    })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Erro ao obter a lista de usuários');
      }
    })
    .then(data => {
      SenhaUsuario = data['2-Senha'];
      ModalEditar.style.display = 'block';
      FocuInputUsuario.focus();
      document.getElementById('InputUsuarioEditar').value = Nome;
      document.getElementById('InputSenhaEditar').value = SenhaUsuario;
      document.getElementById('InputConfirmarSenha').value = SenhaUsuario;
    })
    .catch(error => {
      console.error(error);
    });
  }

  ObterSenha();
});

FecharModalEditar.addEventListener('click', function() {
  ModalEditar.style.display = 'none';
  document.getElementById('InputUsuarioEditar').value = '';
  document.getElementById('InputSenhaEditar').value = '';
});

//-----------------------------------------------------------------------FUNÇÃO PARA EDITAR OS USUÁRIOS---------------------------------------------------------------//
function EditarUsuario() {
  const InputUsuarioEditar = document.getElementById('InputUsuarioEditar');
  const InputSenhaEditar = document.getElementById('InputSenhaEditar');
  const InputConfirmarSenha = document.getElementById('InputConfirmarSenha');

  if (InputUsuarioEditar.value === '' && InputSenhaEditar.value === '' && InputConfirmarSenha.value === '') {
    InputUsuarioEditar.style.borderColor = 'red';
    InputUsuarioEditar.placeholder = 'Campo obrigatório';
    InputSenhaEditar.style.borderColor = 'red';
    InputSenhaEditar.placeholder = 'Campo obrigatório';
    InputConfirmarSenha.style.borderColor = 'red';
    InputConfirmarSenha.placeholder = 'Campo obrigatório';
    setTimeout(function() {
      InputUsuarioEditar.style.borderColor = 'lightgray';
      InputUsuarioEditar.placeholder = '';
      InputSenhaEditar.style.borderColor = 'lightgray';
      InputSenhaEditar.placeholder = '';
      InputConfirmarSenha.style.borderColor = 'lightgray';
      InputConfirmarSenha.placeholder = '';
    }, 5000);
    return;
  }

  if (InputUsuarioEditar.value === '' && InputSenhaEditar.value === '') {
    InputUsuarioEditar.style.borderColor = 'red';
    InputUsuarioEditar.placeholder = 'Campo obrigatório';
    InputSenhaEditar.style.borderColor = 'red';
    InputSenhaEditar.placeholder = 'Campo obrigatório';
    setTimeout(function() {
      InputUsuarioEditar.style.borderColor = 'lightgray';
      InputUsuarioEditar.placeholder = '';
      InputSenhaEditar.style.borderColor = 'lightgray';
      InputSenhaEditar.placeholder = '';
    }, 5000);
    return;
  }

  if (InputUsuarioEditar.value === '' && InputConfirmarSenha.value === '') {
    InputUsuarioEditar.style.borderColor = 'red';
    InputUsuarioEditar.placeholder = 'Campo obrigatório';
    InputConfirmarSenha.style.borderColor = 'red';
    InputConfirmarSenha.placeholder = 'Campo obrigatório';
    setTimeout(function() {
      InputUsuarioEditar.style.borderColor = 'lightgray';
      InputUsuarioEditar.placeholder = '';
      InputConfirmarSenha.style.borderColor = 'lightgray';
      InputConfirmarSenha.placeholder = '';
    }, 5000);
    return;
  }

  if (InputSenhaEditar.value === '' && InputConfirmarSenha.value === '') {
    InputSenhaEditar.style.borderColor = 'red';
    InputSenhaEditar.placeholder = 'Campo obrigatório';
    InputConfirmarSenha.style.borderColor = 'red';
    InputConfirmarSenha.placeholder = 'Campo obrigatório';
    setTimeout(function() {
      InputSenhaEditar.style.borderColor = 'lightgray';
      InputSenhaEditar.placeholder = '';
      InputConfirmarSenha.style.borderColor = 'lightgray';
      InputConfirmarSenha.placeholder = '';
    }, 5000);
    return;
  }

  if (InputUsuarioEditar.value === '') {
    InputUsuarioEditar.style.borderColor = 'red';
    InputUsuarioEditar.placeholder = 'Campo obrigatório';
    setTimeout(function() {
      InputUsuarioEditar.style.borderColor = 'lightgray';
      InputUsuarioEditar.placeholder = '';

    }, 5000);
    return;
  }

  if (InputSenhaEditar.value === '') {
    InputSenhaEditar.style.borderColor = 'red';
    InputSenhaEditar.placeholder = 'Campo obrigatório';
    setTimeout(function() {
      InputSenhaEditar.style.borderColor = 'lightgray';
      InputSenhaEditar.placeholder = '';
    }, 5000);
    return;
  }

  if (InputConfirmarSenha.value === '') {
    InputConfirmarSenha.style.borderColor = 'red';
    InputConfirmarSenha.placeholder = 'Campo obrigatório';
    setTimeout(function() {
      InputConfirmarSenha.style.borderColor = 'lightgray';
      InputConfirmarSenha.placeholder = '';
    }, 5000);
    return;
  }

  if (InputConfirmarSenha.value !== InputSenhaEditar.value) {
    InputConfirmarSenha.style.borderColor = 'red';
    alert("É necessário que as senhas sejam iguais!")
    setTimeout(function() {
      InputConfirmarSenha.style.borderColor = 'lightgray';
    }, 5000);
    return;
  }


  const EdicaoUsuario = {
    nome: InputUsuarioEditar.value,
    senha: InputConfirmarSenha.value
  };

  const checkboxSelecionada = Array.from(checkboxes).find(checkbox => checkbox.checked);
  const linhaSelecionada = checkboxSelecionada.closest('tr');
  const colunas = linhaSelecionada.getElementsByTagName('td');
  const LoginEditar = colunas[1].textContent.toString();
  console.log(LoginEditar)
  
  fetch(`http://192.168.0.183:8000/pcp/api/Usuarios/${LoginEditar}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'a44pcp22'
    },
    body: JSON.stringify(EdicaoUsuario)
  })
    .then(function(response) {
      if (response.ok) {
        // Sucesso ao salvar o usuário
        return response.json();
      } else {
        // Erro ao salvar o usuário
        throw new Error('Erro ao salvar o usuário');
      }
    })
    .then(function(data) {
      console.log(data); // Exibe a resposta completa da API no console
      if (data.message.includes('atualizado com sucesso')) {
        // Usuário criado com sucesso
        alert(data.message);
        ModalEditar.style.display = 'none';
        document.getElementById('InputUsuarioEditar').value = '';
        document.getElementById('InputSenhaEditar').value = '';
        document.getElementById('InputConfirmarSenha').value = '';
        carregarUsuarios();
      }  else {
        // Mensagem desconhecida
        throw new Error('Mensagem desconhecida retornada pela API');
      }
    })
    .catch(function(error) {
      // Erro na requisição ou tratamento dos resultados
      console.error(error);
      // Realizar alguma ação, como exibir uma mensagem de erro
    });
}

// Função para fechar a modal de edição
FecharModalEditar.addEventListener('click', function() {
  ModalEditar.style.display = 'none';
  document.getElementById('InputUsuarioEditar').value = '';
  document.getElementById('InputSenhaEditar').value = '';
  document.getElementById('InputConfirmarSenha').value = '';

});

//-----------------------------   Função Para Excluir ---------------------------------------------------//

const BotaoExcluir = document.getElementById('ButtonRemover');
const ModalExcluir = document.getElementById('ModalExcluir');
const FecharModalExcluir = document.getElementById('FecharModalExcluir');
const Checkboxes = document.getElementsByName('checkboxUsuario');
const UrlApi = 'http://192.168.0.183:8000/pcp/api/Usuarios/';

// Variável global para armazenar o nome do usuário
let nome = '';

// Evento de clique no botão de excluir
BotaoExcluir.addEventListener('click', function() {
  const checkboxSelecionada = Array.from(Checkboxes).find(checkbox => checkbox.checked);
  if (!checkboxSelecionada) {
    alert("Selecione um Usuário!");
    return;
  }

  // Obter a linha selecionada
  const linhaSelecionada = checkboxSelecionada.closest('tr');

  // Obter as células de dados (colunas) da linha selecionada
  const colunas = linhaSelecionada.getElementsByTagName('td');

  // Obter os valores das colunas desejadas
  nome = colunas[1].textContent;

  // Exibir a modal
  ModalExcluir.style.display = 'block';
});

// Função para fechar a modal de exclusão
FecharModalExcluir.addEventListener('click', function() {
  ModalExcluir.style.display = 'none';
  document.getElementById('InputUsuarioEditar').value = '';
  document.getElementById('InputLoginEditar').value = '';
});

// Função para excluir o usuário
function excluirUsuario() {
  nome.toString
  console.log(nome)
  fetch(`UrlApi${nome}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'a44pcp22'
    },
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Erro ao excluir o usuário');
      }
    })
    .then(data => {
      console.log(data);
      nome = ''; // Apagar o valor do nome
      ModalExcluir.style.display = 'none';
    })
    .catch(error => {
      console.error(error);
    ModalExcluir.style.display = 'none';
    });
}

// Evento de clique no botão "Sim" da modal de exclusão
document.getElementById('UsuarioSim').addEventListener('click', function() {
  excluirUsuario(); 
});

// Evento de clique no botão "Não" da modal de exclusão
document.getElementById('UsuarioNão').addEventListener('click', function() {
  ModalExcluir.style.display = 'none';
  document.getElementById('InputUsuarioEditar').value = '';
  document.getElementById('InputLoginEditar').value = '';
});




function carregarUsuarios() {
  fetch('http://192.168.0.183:8000/pcp/api/Usuarios', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'a44pcp22'
    },
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        throw new Error('Erro ao obter a lista de usuários');
      }
    })
    .then(data => {
      totalUsuarios = data.length;
      totalPaginas = Math.ceil(totalUsuarios / 15);

      // Limpa a tabela antes de preenchê-la novamente
      const tabela = document.getElementById('TabelaUsuarios');
      tabela.innerHTML = '';

      // Preenche a tabela com os dados atualizados dos usuários
      criarTabelaUsuarios(data);
    })
    .catch(error => {
      console.error(error);
    });
}