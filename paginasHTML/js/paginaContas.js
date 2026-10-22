document.addEventListener("DOMContentLoaded", async function () {
    const responseUtilizadores = await fetch(`http://localhost:8080/paginaContas`, {
        credentials: "include",
    })
    const jsonUtilizadores = await responseUtilizadores.json()

    const responseContas = await fetch(`http://localhost:8080/contas`, {
        credentials: "include",
    })
    const jsonContas = await responseContas.json()
    
    document.getElementById("email").textContent = jsonUtilizadores["Utilizador"]["email"]

    const titularesUnicos = new Map();

    jsonUtilizadores["Titulares"].forEach(titular => {
        titularesUnicos.set(titular.idTitular, titular);
    });

    console.log(titularesUnicos)

    titularesUnicos.forEach(element => {
        const lista = document.getElementById("listaDonos")

        const donos = document.createElement("li")

        donos.innerHTML = `
            <button id=${element.idTitular} type="button"
                    class="flex w-full items-center gap-2.5 rounded-[10px] px-3.5 py-2.5 text-[15px] text-slate-400 transition-colors hover:bg-slate-800/50 hover:text-slate-200">
                <span class="h-[9px] w-[9px] shrink-0 rounded-full bg-blue-500"></span>
                ${element.titular}
                <span class="ml-auto text-[13px]">4</span>
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

            clone.querySelector('[data-campo="inicial"]').textContent = contas.entidade[0].toUpperCase()
            clone.querySelector('[data-campo="entidade"]').textContent = contas.entidade
            clone.querySelector('[data-campo="email"]').textContent = contas.email
            clone.querySelector('[data-campo="titular"]').textContent = contas.titular
            clone.querySelector('[data-campo="senha"]').textContent = senhaEscondida

            const lista = clone.querySelector("li")
            lista.id = `${contas.idConta}`

            listaContas.appendChild(clone)
        })
    }
})

document.getElementById("pesquisa").addEventListener("input", (event) => {
    console.log(event.target.value)
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

        console.log(resultadoEntidades)

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

            clone.querySelector('[data-campo="inicial"]').textContent = contas.entidade[0].toUpperCase()
            clone.querySelector('[data-campo="entidade"]').textContent = contas.entidade
            clone.querySelector('[data-campo="email"]').textContent = contas.email
            clone.querySelector('[data-campo="titular"]').textContent = contas.titular
            clone.querySelector('[data-campo="senha"]').textContent = senhaEscondida

            const lista = clone.querySelector("li")
            lista.id = `${contas.idConta}`

            listaContas.appendChild(clone)
        })
    }

    const response = await fetch(`http://localhost:8080/contasTitular?titular=${idTitular}`, {
        credentials: "include"
    })

    const jsonContasTitular = await response.json()
    console.log(jsonContasTitular.length)

    if (jsonContasTitular.length === 0) {
        listaContas.innerHTML = ``
        document.getElementById("estadoVazio").classList.remove("hidden")
        document.getElementById("estadoVazio").classList.add("show")
    } else {
        jsonContasTitular.forEach(contas => {
            const listaContas = document.getElementById("listaContas")
            listaContas.innerHTML = ``
            document.getElementById("estadoVazio").classList.remove("show")
            document.getElementById("estadoVazio").classList.add("hidden")
            const template = document.getElementById("modeloCard")
            const clone = template.content.cloneNode(true)

            let senhaEscondida = ""

            for (let i = 0; i <= 8; i++) senhaEscondida += "*"

            clone.querySelector('[data-campo="inicial"]').textContent = contas.entidade[0].toUpperCase()
            clone.querySelector('[data-campo="entidade"]').textContent = contas.entidade
            clone.querySelector('[data-campo="email"]').textContent = contas.email
            clone.querySelector('[data-campo="titular"]').textContent = contas.titular
            clone.querySelector('[data-campo="senha"]').textContent = senhaEscondida

            const lista = clone.querySelector("li")
            lista.id = `${contas.idConta}`

            listaContas.appendChild(clone)
        })
    }
    
})

document.getElementById("botaoAdicionar").addEventListener("click", async () => {
    const form = document.getElementById("formConta")

    form.dataset.aberto = "true"
})

document.getElementById("botaoCancelarFormContas").addEventListener("click", () => {
    const form = document.getElementById("formConta")

    form.dataset.aberto = "false"
})

document.getElementById("guardarConta").addEventListener("click", async (event) => {
    event.preventDefault(); 
    
    const entidade = document.getElementById("inputEntidade").value
    const email = document.getElementById("inputEmail").value
    const senha = document.getElementById("inputSenha").value
    const titular = document.getElementById("campoTitular").value

    await fetch("http://localhost:8080/adicionarConta", {
        method: "POST",
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        body: JSON.stringify({
            entidade: entidade,
            email: email,
            senha: senha,
            idTitular: titular
        }),
    })

    window.location.reload();
})

document.getElementById("sairConta").addEventListener("click", async () => {
    const response = await fetch(`http://localhost:8080/sairConta`, {
        method: "DELETE",
        credentials: "include",
    })

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
            const responseSenha = await fetch(`http://localhost:8080/senhaConta?idConta=${conta.id}`, {
            credentials: "include"
        })

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
})