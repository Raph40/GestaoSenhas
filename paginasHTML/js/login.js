const email = document.getElementById("email")
const password = document.getElementById("password")

document.getElementById("login").addEventListener("click", async event => {
    if (email.value == "") {
        document.getElementById("emailError").textContent = "Campo Email Obrigatorio!"
        email.classList.add("!border-red-500")
    } else {
        document.getElementById("emailError").textContent = ""
        email.classList.remove("!border-red-500")
    }
    if (password.value == "") {
        document.getElementById("passwordError").textContent = "Campo Senha Obrigatorio!"
        password.classList.add("!border-red-500")
    } else {
        document.getElementById("passwordError").textContent = ""
        password.classList.remove("!border-red-500")
    }

    if (email.value && password.value) {
        const response = await fetch("http://localhost:8000/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            body: JSON.stringify({
                email: email.value,
                senha: password.value,
            }),
        })

        const json = await response.json()

        if ("Erro" in json) {
            const mensagemErro = document.getElementById("mensagemErro")
            document.getElementById("mensagemErroTexto").textContent = json["Erro"]
            mensagemErro.classList.remove("hidden");
            mensagemErro.classList.add("flex");

            setTimeout(() => {
                mensagemErro.classList.add("hidden");
                mensagemErro.classList.remove("flex");
            }, 4000);
        } else if ("Sucesso" in json) {
            setTimeout(() => {
                window.location.href = "paginaInicial.html";
            }, 4000);
        }
    }
})