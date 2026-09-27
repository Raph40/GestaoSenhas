const botao = document.getElementById("botaoRegistar")

botao.addEventListener('click', async (e) => {
    e.preventDefault();
    const nome = document.getElementById('nome')
    const email = document.getElementById('email')
    const senha = document.getElementById('senha')
    const confirmarSenha = document.getElementById('confirmarSenha')

    console.log(nome.value)

    if (nome.value === '') {
        const nomeError = document.getElementById('nomeError')
        nomeError.textContent = "Campo Nome Obrigatório!!"
        nome.classList.add("!border-red-500")
    }
    if (email.value === '') {
        const emailError = document.getElementById('emailError')
        emailError.textContent = "Campo Email Obrigatório!!"
        email.classList.add("!border-red-500")
    }
    if (senha.value === '') {
        const senhaError = document.getElementById('senhaError')
        senhaError.textContent = "Campo Senha Obrigatório!!"
        senha.classList.add("!border-red-500")
    }

    if (senha.value !== confirmarSenha.value) {
        const confimarSenhaError = document.getElementById('confimarSenhaError')
        confimarSenhaError.textContent = "Senhas diferentes!!"
        confirmarSenha.classList.add("!border-red-500")
        return
    }

    const response = await fetch('http://localhost:8000/registar', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({
            nome: nome.value,
            email: email.value,
            senha: senha.value,
            confirmarSenha: confirmarSenha.value,
        }),
    })

    const json = await response.json()

    if ("Sucesso" in json) {
    window.location.href = "../paginasHTML/index.html"
    }
})