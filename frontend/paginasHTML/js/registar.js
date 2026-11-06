const botao = document.getElementById("botaoRegistar")

botao.addEventListener('click', async (e) => {
    e.preventDefault();
    const nome = document.getElementById('nome')
    const email = document.getElementById('email')
    const senha = document.getElementById('senha')
    const confirmarSenha = document.getElementById('confirmarSenha')

    if (nome.value === '') {
        const nomeError = document.getElementById('nomeError')
        nomeError.textContent = "Campo Nome Obrigatório!!"
        nome.classList.add("!border-red-500")
    } else {
        const nomeError = document.getElementById('nomeError')
        nomeError.textContent = ""
        nome.classList.remove("!border-red-500")
    }

    if (email.value === '') {
        const emailError = document.getElementById('emailError')
        emailError.textContent = "Campo Email Obrigatório!!"
        email.classList.add("!border-red-500")
    } else {
        const emailError = document.getElementById('emailError')
        emailError.textContent = ""
        email.classList.remove("!border-red-500")
    }
    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!regexEmail.test(email.value)) {
        document.getElementById("emailError").textContent = "Campo Email deve conter um email valido!"
        email.classList.add("!border-red-500")
    }

    if (senha.value === '') {
        const senhaError = document.getElementById('senhaError')
        senhaError.textContent = "Campo Senha Obrigatório!!"
        senha.classList.add("!border-red-500")
    } else {
        const senhaError = document.getElementById('senhaError')
        senhaError.textContent = ""
        senha.classList.remove("!border-red-500")
    }

    if (senha.value !== confirmarSenha.value) {
        const confimarSenhaError = document.getElementById('confimarSenhaError')
        confimarSenhaError.textContent = "Senhas diferentes!!"
        confirmarSenha.classList.add("!border-red-500")
    } else {
        const confimarSenhaError = document.getElementById('confimarSenhaError')
        confimarSenhaError.textContent = ""
        confirmarSenha.classList.remove("!border-red-500")
    }

    const response = await fetch(`http://localhost:8080/emailExistente?email=${encodeURIComponent(email.value)}`)

    const json = await response.json()

    if ("Erro" in json) {
        emailError.textContent = "Email já existe!"
        email.classList.add("!border-red-500")
        return
    }

    if (nome.value && senha.value && senha.value && confirmarSenha.value) {
        const response = await fetch('http://localhost:8080/registar', {
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
            const popEditar = document.getElementById("successModal")
            popEditar.setAttribute('aria-hidden', 'false')
            popEditar.classList.remove("hidden")
            popEditar.classList.add("show")

            document.querySelector(`button[data-modal-toggle="successModal"]`).addEventListener("click", () => {
                document.activeElement.blur()

                popEditar.setAttribute('aria-hidden', 'true')
                popEditar.classList.remove("show");
                popEditar.classList.add("hidden");
            })

            document.getElementById("continuarSuccess").addEventListener("click", () => {
                document.activeElement.blur()

                popEditar.setAttribute('aria-hidden', 'true')
                popEditar.classList.remove("show");
                popEditar.classList.add("hidden");

                window.location.href = "../index.html"
            })
        }
    }
})