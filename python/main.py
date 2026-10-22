import mysql
import connect
import hashlib
import secrets
import uvicorn


from fastapi import FastAPI, Response, Cookie
from pydantic import BaseModel, Field, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta
from typing import Annotated

NOME_COOKIE = "sessao_id"
DURACAO_SESSAO = timedelta(minutes=30)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Registar(BaseModel):
    nome: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=50)
    senha: str = Field(min_length=1, max_length=50)
    confirmarSenha: str = Field(min_length=1, max_length=50)

class Login(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=50)
    senha: str = Field(min_length=1, max_length=50)

class Dono(BaseModel):
    nome: str = Field(min_length=1, max_length=50)

class Conta(BaseModel):
    entidade: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=50)
    senha: str = Field(min_length=1, max_length=50)
    idTitular: int


@app.get("/emailExistente")
async def emailExistente(email: str):
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor()

    emailQuery = "SELECT * FROM utilizadores WHERE email = %s"
    emailValor = (email,)
    mycursor.execute(emailQuery, emailValor)
    email = mycursor.fetchone()

    if email:
        return {"Erro": "Email já utilizado!"}
    else:
        return {"Sucesso": "Email não utilizado!"}

@app.get("/senhaConta")
async def senhaConta(idConta: str, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor()
    tokenHash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()

    mycursor.execute(
        """
            SELECT 
                contas.idContas,
                contas.senha
            FROM gestaocontas.sessao
            INNER JOIN gestaocontas.utilizadores
                ON sessao.Utilizadores_idUtilizadores = utilizadores.idUtilizadores
            INNER JOIN gestaocontas.titular
                ON utilizadores.idUtilizadores = titular.Utilizadores_idUtilizadores
            INNER JOIN gestaocontas.contas
                ON titular.idTitular = contas.Titular_idTitular
            WHERE sessao.idSessao = %s AND contas.IdContas = %s
        """,
        (tokenHash,idConta)
    )

    infSenha = mycursor.fetchall()

    return infSenha

@app.post("/registar")
async def registar(infRegistar: Registar):
    if not infRegistar.nome:
        raise ValueError("Campo nome obrigatorio!!")
    if not isinstance(infRegistar.nome, str):
        raise ValueError("Campo nome é do tipo texto!!")

    if not infRegistar.email:
        raise ValueError("Campo email obrigatorio!!")

    if not infRegistar.senha:
        raise ValueError("Campo senha obrigatorio!!")
    if not isinstance(infRegistar.senha, str):
        raise ValueError("Campo senha é do tipo texto!!")

    if not infRegistar.confirmarSenha:
        raise ValueError("Campo para confirmar a senha obrigatorio!!")
    if not isinstance(infRegistar.confirmarSenha, str):
        raise ValueError("Campo para confirmar a senha é do tipo texto!!")

    if infRegistar.senha != infRegistar.confirmarSenha:
        raise ValueError("Senhas diferentes!!")

    try:
        ph = PasswordHasher()
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor()

        registarQuery = 'INSERT INTO utilizadores (nome, email, senha) VALUES (%s, %s, %s)'
        registarInf = (infRegistar.nome, infRegistar.email, ph.hash(infRegistar.senha))
        mycursor.execute(registarQuery, registarInf)
        mydb.commit()
    except mysql.connector.Error as err:
        raise ValueError(err)
    else:
        mycursor.close()
        mydb.close()
        return {"Sucesso": "Conta criada com sucesso!!"}

@app.post("/login")
async def login(infLogin: Login, response: Response):
    ph = PasswordHasher()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    perfilQuerry = "SELECT * FROM utilizadores WHERE email = %s"
    perfilValor = (infLogin.email,)
    mycursor.execute(perfilQuerry, perfilValor)
    conta = mycursor.fetchone()

    try:
        ph.verify(conta[3], infLogin.senha)

        mycursorInsert = mydb.cursor(buffered=True)
        tokenSegredo = secrets.token_urlsafe(32)
        tokenHash = hashlib.sha256(tokenSegredo.encode()).hexdigest()
        dataExpira = datetime.now() + DURACAO_SESSAO
        sessaoQuerry = "INSERT INTO sessao (idSessao, Utilizadores_idUtilizadores, criada, expira) VALUES (%s, %s, %s, %s)"
        sessaoValores = (tokenHash, conta[0], datetime.now(), dataExpira)
        mycursorInsert.execute(sessaoQuerry, sessaoValores)
        mydb.commit()
        mycursorInsert.close()

        response.set_cookie(
            key=NOME_COOKIE,
            value=tokenSegredo,
            httponly=True,
            samesite="none",
            secure=True,
            max_age=int(DURACAO_SESSAO.total_seconds()),
            path="/",
        )

        return {"Sucesso": "Login realizado com sucesso!"}
    except VerifyMismatchError:
        mycursor.close()
        return {"Erro": "Senha incorreta!"}

@app.get("/paginaContas")
async def paginaContas(nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    tokenHash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()

    mycursor.execute(
        """
            SELECT
                utilizadores.idUtilizadores,
                utilizadores.nome,
                utilizadores.email,
                titular.idTitular,
                titular.Titular,
                sessao.expira
            FROM gestaocontas.sessao
            INNER JOIN gestaocontas.utilizadores
                ON sessao.Utilizadores_idUtilizadores = utilizadores.idUtilizadores
            INNER JOIN gestaocontas.titular
                ON utilizadores.idUtilizadores = titular.Utilizadores_idUtilizadores
            WHERE sessao.idSessao = %s;
        """,
        (tokenHash,)
    )
    infUtilizador = mycursor.fetchall()

    print(infUtilizador)

    infUtilizadorJSON = {
        "Utilizador": {
            "id": infUtilizador[0][0],
            "nome": infUtilizador[0][1],
            "email": infUtilizador[0][2],
            "dataExpiracao": infUtilizador[0][4]
        },
        "Titulares": [{
            "idTitular": i[3],
            "titular": i[4]
        } for i in infUtilizador],
    }

    print(infUtilizadorJSON)

    return infUtilizadorJSON

@app.get("/contas")
async def contas(nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    tokenHash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
    mycursor.execute(
        """
            SELECT
                contas.idContas,
                contas.entidade,
                contas.email,
                titular.titular
            FROM gestaocontas.sessao
            INNER JOIN gestaocontas.utilizadores
                ON sessao.Utilizadores_idUtilizadores = utilizadores.idUtilizadores
            INNER JOIN gestaocontas.titular
                ON utilizadores.idUtilizadores = titular.Utilizadores_idUtilizadores
            INNER JOIN gestaocontas.contas
                ON titular.idTitular = contas.Titular_idTitular
            WHERE sessao.idSessao = %s;
        """,
        (tokenHash,)
    )
    infContas = mycursor.fetchall()

    infContasJSON = [{
        "idConta": i[0],
        "entidade": i[1],
        "email": i[2],
        "titular": i[3]
    } for i in infContas]

    return infContasJSON

@app.get("/contasTitular")
async def contasTitular(titular: int, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    tokenHash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
    mycursor.execute(
        """
            SELECT
                contas.idContas,
                contas.entidade,
                contas.email,
                titular.titular
            FROM gestaocontas.sessao
            INNER JOIN gestaocontas.utilizadores
                ON sessao.Utilizadores_idUtilizadores = utilizadores.idUtilizadores
            INNER JOIN gestaocontas.titular
                ON utilizadores.idUtilizadores = titular.Utilizadores_idUtilizadores
            INNER JOIN gestaocontas.contas
                ON titular.idTitular = contas.Titular_idTitular
            WHERE sessao.idSessao = %s AND contas.idContas = %s;
        """,
        (tokenHash,titular)
    )
    infContas = mycursor.fetchall()

    infContasJSON = [{
        "idConta": i[0],
        "entidade": i[1],
        "email": i[2],
        "titular": i[3]
    } for i in infContas]

    return infContasJSON
    
@app.post("/criarDono")
async def criarDono(dono: Dono, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    tokenHash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    try:
        mycursor.execute(
            """
                SELECT Utilizadores_idUtilizadores FROM sessao WHERE idSessao = %s
            """,
            (tokenHash,)
        )
        infUtilizador = mycursor.fetchone()

        mycursor.execute(
            """
                INSERT INTO titular (Titular,Utilizadores_idUtilizadores) VALUES (%s,%s)
            """,
            (dono.nome,infUtilizador[0])
        )
        mydb.commit()
    except mysql.connector.Error as err:
            raise ValueError(err)
    else:
        mycursor.close()
        mydb.close()
        return {"Sucesso": "Titular adicionado com sucesso!!"}

@app.post("/adicionarConta")
async def adicionarConta(infConta: Conta, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    tokenHash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute(
        """
            SELECT utilizadores_idUtilizadores FROM sessao WHERE idSessao = %s
        """,
        (tokenHash,)
    )

    resultadoId = mycursor.fetchall()

    mycursor.execute(
        """
            INSERT INTO contas (utilizadores_idUtilizadores, entidade, email, senha, Titular_idTitular) VALUES (%s,%s,%s,%s,%s)
        """,
        (resultadoId[0][0], infConta.entidade, infConta.email, infConta.senha, infConta.idTitular)
    )

    mydb.commit()

@app.delete("/sairConta")
async def sairConta(response: Response, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    tokenHash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute(
        """
            DELETE FROM sessao WHERE idSessao = %s
        """,
        (tokenHash,)
    )

    mydb.commit()

    response.delete_cookie(
        key=NOME_COOKIE,
        path="/"
        )

    return {"Sucesso": "Sessao terminada com sucesso!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)