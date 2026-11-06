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
    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    if (!regexEmail.test(email.value)) {
        document.getElementById("emailError").textContent = "Campo Email deve conter um email valido!"
        email.classList.add("!border-red-500")
    }
    if (password.value == "") {
        document.getElementById("passwordError").textContent = "Campo Senha Obrigatorio!"
        password.classList.add("!border-red-500")
    } else {
        document.getElementById("passwordError").textContent = ""
        password.classList.remove("!border-red-500")
    }

    if (email.value && password.value) {
        const response = await fetch("http://localhost:8081/login", {
            method: "POST",
            credentials: "include",
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
        console.log(json)

        if ("Erro" in json) {
            const passwordError = document.getElementById("passwordError")
            passwordError.textContent = "Senha Incorreta"
            passwordError.classList.add("!border-red-500")
        } else if ("Sucesso" in json) {
            window.location.href = "../paginaInicial.html"
        }
    }
})