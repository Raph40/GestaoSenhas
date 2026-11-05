document.addEventListener("DOMContentLoaded", async function () {
    const responseUtilizadores = await fetch(`http://localhost:8080/paginaContas`, {
        credentials: "include",
    })

    if (!responseUtilizadores.ok) {
        window.location.href = '/index.html'
    }

    const jsonUtilizadores = await responseUtilizadores.json()

    const responseContas = await fetch(`http://localhost:8080/contas`, {
        credentials: "include",
    })

    if (!responseContas.ok) {
        window.location.href = '/index.html'
    }
    const jsonContas = await responseContas.json()

    document.getElementById("contagemContas").innerText = `${jsonUtilizadores["Titulares"].length} contas de ${jsonContas.length} titulares`
    document.getElementById("contidadeTitulares").innerText = `${jsonUtilizadores["Titulares"].length}`

    document.getElementById("email").textContent = jsonUtilizadores["Utilizador"]["email"]

    const contagemContas = {}

    jsonContas.forEach(conta => {
        contagemContas[conta["titular"]] = (contagemContas[conta["titular"]] || 0) + 1
    })

    const titularesUnicos = new Map()

    jsonUtilizadores["Titulares"].forEach(titular => {
        titularesUnicos.set(titular.idTitular, titular)
    });

    titularesUnicos.forEach(element => {
        const lista = document.getElementById("listaDonos")

        const donos = document.createElement("li")

        donos.innerHTML = `
            <button id=${element.idTitular} type="button"
                    class="flex w-full items-center gap-2.5 rounded-[10px] px-3.5 py-2.5 text-[15px] text-slate-400 transition-colors hover:bg-slate-800/50 hover:text-slate-200">
                <span class="h-[9px] w-[9px] shrink-0 rounded-full bg-blue-500"></span>
                ${element.titular}
                <span class="ml-auto text-[13px]">${contagemContas[element.titular] || 0}</span>
            </button>
        `

        lista.appendChild(donos)

        const listaForm = document.getElementById("campoTitular")

        const donosForm = document.createElement("option")

        donosForm.value = element.idTitular
        donosForm.className = "bg-[#111c2e] text-slate-200"
        donosForm.textContent = element.titular

        listaForm.appendChild(donosForm)
    });

    const contasUnicas = new Map();

    jsonContas.forEach(conta => {
        contasUnicas.set(conta.idConta, conta);
    });

    if (contasUnicas.size === 0) {
        const idSemContas = document.getElementById("estadoVazio")
        idSemContas.classList.remove("hidden")
        idSemContas.classList.add("show")
    } else {
        contasUnicas.forEach(contas => {
            const listaContas = document.getElementById("listaContas")
            const template = document.getElementById("modeloCard")
            const clone = template.content.cloneNode(true)

            let senhaEscondida = ""

            for (let i = 0; i <= 8; i++) senhaEscondida += "*"

            template_informacao(clone, contas.entidade, contas.email, contas.idTitular, contas.titular, senhaEscondida)

            const lista = clone.querySelector("li")
            lista.id = `${contas.idConta}`

            listaContas.appendChild(clone)
        })
    }
})

document.getElementById("pesquisa").addEventListener("input", (event) => {
    const inf = document.getElementById("listaContas")
    const infListas = inf.querySelectorAll("li")

    const arrayEntidades = []

    infListas.forEach((li) => {
        const entidadeCampo = li.querySelector(`[data-campo="entidade"]`)
        const entidadeNome = entidadeCampo.textContent.toLowerCase()

        arrayEntidades.push(entidadeNome)
    })

    const resultadoEntidades = arrayEntidades.filter(items => items.includes(event.target.value))

    const listaContas = document.querySelector("#listaContas")

    Array.from(listaContas.children).forEach(entidade => {
        const entidadesCampo = entidade.querySelector(`[data-campo="entidade"]`).textContent.toLowerCase()

        if (resultadoEntidades.includes(entidadesCampo)) {
            entidade.classList.remove("hidden")
        } else {
            entidade.classList.add("hidden")
        }

        if (event.target.value.length === 0) {
            entidade.classList.remove("hidden")
        }
    })
})

document.getElementById("listaDonos").addEventListener("click", async (event) => {
    const botaoVer = event.target.closest("button")
    const idTitular = botaoVer.id
    const listaContas = document.getElementById("listaContas")

    if (idTitular === "contasTodos") {
        const listaContas = document.getElementById("listaContas")
        listaContas.innerHTML = ``

        const responseContas = await fetch(`http://localhost:8080/contas`, {
            credentials: "include",
        })

        if (!responseContas.ok) {
            window.location.href = '/index.html'
        }

        const jsonContas = await responseContas.json()

        if (jsonContas.length > 0) {
            const divLista = document.getElementById("estadoVazio")
            divLista.classList.add("hidden")
        } else {
            const divLista = document.getElementById("estadoVazio")
            divLista.classList.remove("show")
        }

        jsonContas.forEach(contas => {
            const listaContas = document.getElementById("listaContas")
            const template = document.getElementById("modeloCard")
            const clone = template.content.cloneNode(true)

            let senhaEscondida = ""

            for (let i = 0; i <= 8; i++) senhaEscondida += "*"

            template_informacao(clone, contas.entidade, contas.email, contas.idTitular, contas.titular, senhaEscondida)

            const lista = clone.querySelector("li")
            lista.id = `${contas.idConta}`

            listaContas.appendChild(clone)
        })
    } else {
        const response = await fetch(`http://localhost:8080/contasTitular?titular=${idTitular}`, {
            credentials: "include"
        })

        if (!response.ok) {
            window.location.href = '/index.html'
        }

        const jsonContasTitular = await response.json()

        if (jsonContasTitular.length === 0) {
            listaContas.innerHTML = ``
            document.getElementById("estadoVazio").classList.remove("hidden")
            document.getElementById("estadoVazio").classList.add("show")
        } else {
            listaContas.innerHTML = ``
            jsonContasTitular.forEach(contas => {
                const listaContas = document.getElementById("listaContas")
                document.getElementById("estadoVazio").classList.remove("show")
                document.getElementById("estadoVazio").classList.add("hidden")
                const template = document.getElementById("modeloCard")
                const clone = template.content.cloneNode(true)

                let senhaEscondida = ""

                for (let i = 0; i <= 8; i++) senhaEscondida += "*"

                template_informacao(clone, contas.entidade, contas.email, contas.idTitular, contas.titular, senhaEscondida)

                const lista = clone.querySelector("li")
                lista.id = `${contas.idConta}`

                listaContas.appendChild(clone)
            })
        }
    }
})

document.getElementById("botaoAdicionar").addEventListener("click", async () => {
    const form = document.getElementById("formConta")
    form.querySelector("#tituloForm").textContent = "Nova Conta"
    form.dataset.aberto = "true"
})

document.getElementById("botaoCancelarFormContas").addEventListener("click", () => {
    const form = document.getElementById("formConta")
    const entidade = document.getElementById("inputEntidade")
    const email = document.getElementById("inputEmail")
    const senha = document.getElementById("inputSenha")
    const titular = document.getElementById("campoTitular")

    document.getElementById("formConta").dataset.id = ""

    entidade.value = ""
    email.value = ""
    senha.value = ""
    titular.value = ""

    const entidadeError = document.getElementById("entidadeError")
    const emailError = document.getElementById("emailError")
    const senhaError = document.getElementById("senhaError")
    const titularError = document.getElementById("titularError")

    entidadeError.textContent = ""
    entidade.classList.remove("!border-red-500")

    emailError.textContent = ""
    email.classList.remove("!border-red-500")

    senhaError.textContent = ""
    senha.classList.remove("!border-red-500")

    titularError.textContent = ""
    titular.classList.remove("!border-red-500")

    if (form.querySelector('#alterarConta')) {
        form.querySelector('#alterarConta').textContent = "Guardar Conta"
        form.querySelector('#alterarConta').id = "guardarConta"
    }

    form.dataset.aberto = "false"
})

document.getElementById("guardarConta").addEventListener("click", async (event) => {
    event.preventDefault();

    const botao = event.currentTarget

    if (botao.id === "guardarConta") {
        const entidade = document.getElementById("inputEntidade")
        const email = document.getElementById("inputEmail")
        const senha = document.getElementById("inputSenha")
        const titular = document.getElementById("campoTitular")

        if (entidade.value === "") {
            const entidadeError = document.getElementById("entidadeError")
            entidadeError.textContent = "Campo entidade obrigatório"
            entidade.classList.add("!border-red-500")
        } else {
            entidadeError.textContent = ""
            entidade.classList.remove("!border-red-500")
        }

        if (email.value === "") {
            const emailError = document.getElementById("emailError")
            emailError.textContent = "Campo email obrigatório"
            email.classList.add("!border-red-500")
        } else {
            emailError.textContent = ""
            email.classList.remove("!border-red-500")
        }

        if (senha.value === "") {
            const senhaError = document.getElementById("senhaError")
            senhaError.textContent = "Campo senha obrigatório"
            senha.classList.add("!border-red-500")
        } else {
            senhaError.textContent = ""
            senha.classList.remove("!border-red-500")
        }

        if (titular.value === "") {
            const titularError = document.getElementById("titularError")
            titularError.textContent = "Campo titular obrigatório"
            titular.classList.add("!border-red-500")
        } else {
            titularError.textContent = ""
            titular.classList.remove("!border-red-500")

            const response = await fetch("http://localhost:8080/adicionarConta", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                body: JSON.stringify({
                    entidade: entidade.value,
                    email: email.value,
                    senha: senha.value,
                    idTitular: titular.value
                }),
            })

            if (!response.ok) {
                window.location.href = '/index.html'
            }

            const popEditar = document.getElementById("successModal")
            popEditar.setAttribute('aria-hidden', 'false')
            popEditar.classList.remove("hidden")
            popEditar.classList.add("show")

            document.querySelector(`button[data-modal-toggle="successModal"]`).addEventListener("click", () => {
                document.activeElement.blur()

                popEditar.setAttribute('aria-hidden', 'true')
                popEditar.classList.remove("show");
                popEditar.classList.add("hidden");

                window.location.reload()
            })

            document.getElementById("continuarSuccess").addEventListener("click", () => {
                document.activeElement.blur()

                popEditar.setAttribute('aria-hidden', 'true')
                popEditar.classList.remove("show");
                popEditar.classList.add("hidden");

                window.location.reload()
            })

            window.location.reload();
        }
    } else if (botao.id === "alterarConta") {
        const id_conta = document.querySelector("#formNovaConta").dataset.id
        const entidade = document.getElementById("inputEntidade").value
        const email = document.getElementById("inputEmail").value
        const senha = document.getElementById("inputSenha").value
        const titular = document.getElementById("campoTitular").value

        const response = await fetch(`http://localhost:8080/editarConta`, {
            method: "PUT",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify({
                id_conta: id_conta,
                entidade: entidade,
                email: email,
                senha: senha,
                idTitular: titular
            }),
        })

        if (!response.ok) {
            window.location.href = '/index.html'
        }

        const popEditar = document.getElementById("successModal")
        popEditar.setAttribute('aria-hidden', 'false')
        popEditar.classList.remove("hidden")
        popEditar.classList.add("show")

        document.querySelector(`button[data-modal-toggle="successModal"]`).addEventListener("click", () => {
            document.activeElement.blur()

            popEditar.setAttribute('aria-hidden', 'true')
            popEditar.classList.remove("show");
            popEditar.classList.add("hidden");

            window.location.reload()
        })

        document.getElementById("continuarSuccess").addEventListener("click", () => {
            document.activeElement.blur()

            popEditar.setAttribute('aria-hidden', 'true')
            popEditar.classList.remove("show");
            popEditar.classList.add("hidden");

            window.location.reload()
        })
    }
})

document.getElementById("sairConta").addEventListener("click", async () => {
    const response = await fetch(`http://localhost:8080/sairConta`, {
        method: "DELETE",
        credentials: "include",
    })

    if (!response.ok) {
        window.location.href = '/index.html'
    }

    const json = await response.json()

    if ("Sucesso" in json) {
        window.location.href = '/index.html'
    }
})

document.getElementById("adicionarDonos").addEventListener("click", () => {
    const donos = document.getElementById("modalDono")

    donos.classList.remove("hidden")
    donos.classList.add("flex")
})

document.getElementById("cancelarDono").addEventListener("click", () => {
    const donos = document.getElementById("modalDono")

    donos.classList.add("hidden")
    donos.classList.remove("flex");
})

document.getElementById("criarDono").addEventListener("click", async (event) => {
    event.preventDefault()
    const dono = document.getElementById("nomeDono")
    const response = await fetch(`http://localhost:8080/criarDono`, {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({
            nome: dono.value
        }),
    })

    if (!response.ok) {
        window.location.href = '/index.html'
    }

    const json = await response.json()

    if ("Sucesso" in json) {
        const donos = document.getElementById("modalDono")
        donos.classList.add("hidden")
    }
    window.location.reload();
})

document.getElementById("listaContas").addEventListener("click", async (event) => {
    const botaoVer = event.target.closest("button")
    const conta = botaoVer.closest("li")

    const acao = botaoVer.dataset.campo

    if (acao === "ver") {
        const imagemVer = botaoVer.querySelector("#iconeVer")
        const imagemEsconder = botaoVer.querySelector("#iconeEsconder")

        if (imagemEsconder.classList.contains("hidden")) {
            const responseSenha = await fetch(`http://localhost:8080/senhaConta?id_conta=${conta.id}`, {
                credentials: "include"
            })

            if (!responseSenha.ok) {
                window.location.href = '/index.html'
            }

            const jsonSenha = await responseSenha.json()

            const pSenha = conta.querySelector('p[data-campo="senha"]');
            pSenha.textContent = jsonSenha[0][1]


            imagemVer.classList.add("hidden")
            imagemEsconder.classList.remove("hidden")

        } else {

            let senhaEscondida = ""

            for (let i = 0; i <= 8; i++) senhaEscondida += "*"

            const pSenha = conta.querySelector('p[data-campo="senha"]');
            pSenha.textContent = senhaEscondida

            imagemVer.classList.remove("hidden")
            imagemEsconder.classList.add("hidden")
        }
    }

    if (acao === "editar") {
        const form = document.getElementById("formConta")

        form.dataset.aberto = "true"

        form.querySelector('#guardarConta').textContent = "Guardar Alterações"
        form.querySelector('#guardarConta').id = "alterarConta"

        document.getElementById("formNovaConta").dataset.id = conta.id

        const responseSenha = await fetch(`http://localhost:8080/senhaConta?id_conta=${conta.id}`, {
            credentials: "include"
        })

        if (!responseSenha.ok) {
            window.location.href = '/index.html'
        }

        const jsonSenha = await responseSenha.json()

        const entidade = form.querySelector("#inputEntidade").value = conta.querySelector('p[data-campo="entidade"]').textContent
        const email = form.querySelector("#inputEmail").value = conta.querySelector('p[data-campo="email"]').textContent
        const senha = form.querySelector("#inputSenha").value = jsonSenha[0][1]
        const titular = form.querySelector("#campoTitular").value = conta.querySelector('span[data-campo="titular"]').id

        if (entidade.value === "") {
            const entidadeError = document.getElementById("entidadeError")
            entidadeError.textContent = "Campo entidade obrigatório"
            entidade.classList.add("!border-red-500")
        } else {
            entidadeError.textContent = ""
            entidade.classList.remove("!border-red-500")
        }

        if (email.value === "") {
            const emailError = document.getElementById("emailError")
            emailError.textContent = "Campo email obrigatório"
            email.classList.add("!border-red-500")
        } else {
            emailError.textContent = ""
            email.classList.remove("!border-red-500")
        }

        if (senha.value === "") {
            const senhaError = document.getElementById("senhaError")
            senhaError.textContent = "Campo senha obrigatório"
            senha.classList.add("!border-red-500")
        } else {
            senhaError.textContent = ""
            senha.classList.remove("!border-red-500")
        }

        if (titular.value === "") {
            const titularError = document.getElementById("titularError")
            titularError.textContent = "Campo titular obrigatório"
            titular.classList.add("!border-red-500")
        } else {
            titularError.textContent = ""
            titular.classList.remove("!border-red-500")
        }
    }

    if (acao === "apagar") {
        const entidade = conta.querySelector('p[data-campo="entidade"]').textContent
        const email = conta.querySelector('p[data-campo="email"]').textContent
        const titular = conta.querySelector('span[data-campo="titular"]').textContent
        const apagar = document.getElementById("modalApagar")
        document.getElementById("textoApagar").textContent = `Vais apagar a conta ${entidade} que contem o email ${email} do titular ${titular}. Esta ação não pode ser desfeita.`

        apagar.classList.remove("hidden")
        apagar.classList.add("flex")

        document.getElementById("btnCancelarApagar").addEventListener("click", () => {
            apagar.classList.remove("flex")
            apagar.classList.add("hidden")
        })

        document.getElementById("btnConfirmarApagar").addEventListener("click", async () => {
            const response = await fetch(`http://localhost:8080/deleteConta?id_conta=${conta.id}`, {
                credentials: "include",
                method: "DELETE"
            })

            if (!response.ok) {
                window.location.href = '/index.html'
            }

            window.location.reload();
        })
    }
})

function template_informacao(clone, entidade, email, idTitular, titular, senhaEscondida) {
    clone.querySelector('[data-campo="inicial"]').textContent = entidade[0].toUpperCase()
    clone.querySelector('[data-campo="entidade"]').textContent = entidade
    clone.querySelector('[data-campo="email"]').textContent = email
    clone.querySelector('[data-campo="titular"]').textContent = titular
    clone.querySelector('[data-campo="titular"]').id = idTitular
    clone.querySelector('[data-campo="senha"]').textContent = senhaEscondida
}