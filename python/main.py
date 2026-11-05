import mysql
import connect
import hashlib
import secrets
import uvicorn

from fastapi import FastAPI, Response, Cookie, APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, EmailStr
from fastapi.middleware.cors import CORSMiddleware
from argon2 import PasswordHasher
from datetime import datetime, timedelta
from typing import Annotated
from mysql.connector import IntegrityError, DataError, OperationalError, DatabaseError, OperationalError, ProgrammingError, DatabaseError

NOME_COOKIE = "sessao_id"
DURACAO_SESSAO = timedelta(minutes=30)

def verificacao_cookie(response: Response, nome_do_cookie: str | None = Cookie(default=None, alias=NOME_COOKIE)):
    if nome_do_cookie == None:
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)

        mycursor.execute(
            """
                DELETE FROM sessao WHERE expira < NOW()
            """
        )

        mydb.commit()

        response.delete_cookie(
            key=NOME_COOKIE,
            path="/"
        )

        raise HTTPException(status_code=401, detail="Credenciais inválidas")

app = FastAPI()

privado = APIRouter(dependencies=[Depends(verificacao_cookie)])
publico = APIRouter()

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

class EditarConta(BaseModel):
    id_conta: int
    entidade: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(min_length=1, max_length=50)
    senha: str = Field(min_length=1, max_length=50)
    idTitular: int

@publico.get("/emailExistente")
async def email_existente(email: str):
    try:
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor()

        email_query = "SELECT * FROM utilizadores WHERE email = %s"
        email_valor = (email,)
        mycursor.execute(email_query, email_valor)
        email = mycursor.fetchone()

        if email:
            return {"Erro": "Email já utilizado!"}
        else:
            return {"Sucesso": "Email não utilizado!"}
    except OperationalError:
        return {"Erro"}
    except ProgrammingError:
        return {"Erro"}
    except DatabaseError:
        return {"Erro"}
    finally:
        mycursor.close()


@privado.get("/senhaConta")
async def senha_conta(id_conta: str, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor()
        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()

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
            (token_hash,id_conta)
        )

        inf_senha = mycursor.fetchall()
        return inf_senha
    except OperationalError:
        return {"Erro"}
    except ProgrammingError:
        return {"Erro"}
    except DatabaseError:
        return {"Erro"}
    finally:
        mycursor.close()

@publico.post("/registar")
async def registar(inf_registar: Registar):
    if not inf_registar.nome:
        raise ValueError("Campo nome obrigatorio!!")
    if not isinstance(inf_registar.nome, str):
        raise ValueError("Campo nome é do tipo texto!!")

    if not inf_registar.email:
        raise ValueError("Campo email obrigatorio!!")

    if not inf_registar.senha:
        raise ValueError("Campo senha obrigatorio!!")
    if not isinstance(inf_registar.senha, str):
        raise ValueError("Campo senha é do tipo texto!!")

    if not inf_registar.confirmarSenha:
        raise ValueError("Campo para confirmar a senha obrigatorio!!")
    if not isinstance(inf_registar.confirmarSenha, str):
        raise ValueError("Campo para confirmar a senha é do tipo texto!!")

    if inf_registar.senha != inf_registar.confirmarSenha:
        raise ValueError("Senhas diferentes!!")

    try:
        ph = PasswordHasher()
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor()

        registar_query = 'INSERT INTO utilizadores (nome, email, senha) VALUES (%s, %s, %s)'
        registar_inf = (inf_registar.nome, inf_registar.email, ph.hash(inf_registar.senha))
        mycursor.execute(registar_query, registar_inf)
        mydb.commit()
        return {"Sucesso": "Conta criada com sucesso!!"}
    except IntegrityError:
        mydb.rollback
    except DataError:
        mydb.rollback
    except OperationalError:
        mydb.rollback
    except DatabaseError:
        mydb.rollback
    finally:
        mycursor.close()
        mydb.close()
        

@publico.post("/login")
async def login(inf_login: Login, response: Response):
    ph = PasswordHasher()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    perfil_querry = "SELECT * FROM utilizadores WHERE email = %s"
    perfil_valor = (inf_login.email,)
    mycursor.execute(perfil_querry, perfil_valor)
    conta = mycursor.fetchone()

    try:
        ph.verify(conta[3], inf_login.senha)

        mycursor_insert = mydb.cursor(buffered=True)
        token_segredo = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token_segredo.encode()).hexdigest()
        data_expira = datetime.now() + DURACAO_SESSAO
        sessao_querry = "INSERT INTO sessao (idSessao, Utilizadores_idUtilizadores, criada, expira) VALUES (%s, %s, %s, %s)"
        sessao_valores = (token_hash, conta[0], datetime.now(), data_expira)
        mycursor_insert.execute(sessao_querry, sessao_valores)
        mydb.commit()
        mycursor_insert.close()

        response.set_cookie(
            key=NOME_COOKIE,
            value=token_segredo,
            httponly=True,
            samesite="none",
            secure=True,
            max_age=int(DURACAO_SESSAO.total_seconds()),
            path="/",
        )

        return {"Sucesso": "Login realizado com sucesso!"}
    except IntegrityError:
        mydb.rollback
        return {"Erro"}
    except DataError:
        mydb.rollback
        return {"Erro"}
    except OperationalError:
        mydb.rollback
        return {"Erro"}
    except DatabaseError:
        mydb.rollback
        return {"Erro"}
    finally:
        mycursor.close()
        mydb.close()

@privado.get("/paginaContas")
async def pagina_contas(nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)

        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()

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
            (token_hash,)
        )
        inf_utilizador = mycursor.fetchall()

        inf_utilizador_json = {
            "Utilizador": {
                "id": inf_utilizador[0][0],
                "nome": inf_utilizador[0][1],
                "email": inf_utilizador[0][2],
                "dataExpiracao": inf_utilizador[0][4]
            },
            "Titulares": [{
                "idTitular": i[3],
                "titular": i[4]
            } for i in inf_utilizador],
        }
        return inf_utilizador_json
    except OperationalError:
        return {"Erro"}
    except ProgrammingError:
        return {"Erro"}
    except DatabaseError:
        return {"Erro"}
    finally:
        mycursor.close()
        mydb.close()

@privado.get("/contas")
async def contas(nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)

        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
        mycursor.execute(
            """
                SELECT
                    contas.idContas,
                    contas.entidade,
                    contas.email,
                    titular.idTitular,
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
            (token_hash,)
        )
        inf_contas = mycursor.fetchall()

        inf_contas_json = [{
            "idConta": i[0],
            "entidade": i[1],
            "email": i[2],
            "idTitular": i[3],
            "titular": i[4]
        } for i in inf_contas]

        return inf_contas_json
    except OperationalError:
        return {"Erro"}
    except ProgrammingError:
        return {"Erro"}
    except DatabaseError:
        return {"Erro"}
    finally:
        mycursor.close()
        mydb.close()

@privado.get("/contasTitular")
async def contas_titular(titular: int, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)

        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
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
                WHERE sessao.idSessao = %s AND contas.Titular_idTitular = %s;
            """,
            (token_hash,titular)
        )
        inf_contas = mycursor.fetchall()

        inf_contas_json = [{
            "idConta": i[0],
            "entidade": i[1],
            "email": i[2],
            "titular": i[3]
        } for i in inf_contas]
        
        print(inf_contas_json)

        return inf_contas_json
    except OperationalError:
        return {"Erro"}
    except ProgrammingError:
        return {"Erro"}
    except DatabaseError:
        return {"Erro"}
    finally:
        mycursor.close()
        mydb.close()
    
@privado.post("/criarDono")
async def criar_dono(dono: Dono, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor(buffered=True)

    try:
        mycursor.execute(
            """
                SELECT Utilizadores_idUtilizadores FROM sessao WHERE idSessao = %s
            """,
            (token_hash,)
        )
        inf_utilizador = mycursor.fetchone()

        mycursor.execute(
            """
                INSERT INTO titular (Titular,Utilizadores_idUtilizadores) VALUES (%s,%s)
            """,
            (dono.nome,inf_utilizador[0])
        )
        mydb.commit()

        return {"Sucesso": "Titular adicionado com sucesso!!"}
    except IntegrityError:
        mydb.rollback
    except DataError:
        mydb.rollback
    except OperationalError:
        mydb.rollback
    except DatabaseError:
        mydb.rollback
    finally:
        mycursor.close()
        mydb.close()
        

@privado.post("/adicionarConta")
async def adicionar_conta(inf_conta: Conta, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)

        mycursor.execute(
            """
                SELECT utilizadores_idUtilizadores FROM sessao WHERE idSessao = %s
            """,
            (token_hash,)
        )

        resultado_id = mycursor.fetchall()

        mycursor.execute(
            """
                INSERT INTO contas (utilizadores_idUtilizadores, entidade, email, senha, Titular_idTitular) VALUES (%s,%s,%s,%s,%s)
            """,
            (resultado_id[0][0], inf_conta.entidade, inf_conta.email, inf_conta.senha, inf_conta.idTitular)
        )

        mydb.commit()
    except IntegrityError:
        mydb.rollback
    except DataError:
        mydb.rollback
    except OperationalError:
        mydb.rollback
    except DatabaseError:
        mydb.rollback
    finally:
        mycursor.close()
        mydb.close()

@privado.put("/editarConta")
async def editar_conta(editar: EditarConta, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)

        mycursor.execute(
            """
            UPDATE gestaocontas.contas AS contas
            INNER JOIN gestaocontas.titular AS titular 
                ON contas.Titular_idTitular = titular.idTitular
            INNER JOIN gestaocontas.utilizadores AS utilizadores 
                ON titular.Utilizadores_idUtilizadores = utilizadores.idUtilizadores
            INNER JOIN gestaocontas.sessao AS sessao 
                ON sessao.Utilizadores_idUtilizadores = utilizadores.idUtilizadores
            SET
                contas.entidade = %s,
                contas.email = %s,
                contas.senha = %s,
                contas.Titular_idTitular = %s
            WHERE sessao.idSessao = %s AND contas.idContas = %s;
            """,
            (editar.entidade, editar.email, editar.senha, editar.idTitular, token_hash, editar.id_conta)
        )

        mydb.commit()

        return {"Sucesso": "Dados atualizados com sucesso!!"}
    except IntegrityError:
        mydb.rollback
    except DataError:
        mydb.rollback
    except OperationalError:
        mydb.rollback
    except DatabaseError:
        mydb.rollback
    finally:
        mycursor.close()
        mydb.close()

@privado.delete("/deleteConta")
async def delete_conta(id_conta: int, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)
        
        mycursor.execute(
            """
                DELETE FROM gestaocontas.contas
                WHERE idContas = %s
                AND Utilizadores_idUtilizadores = (
                    SELECT Utilizadores_idUtilizadores
                    FROM gestaocontas.sessao
                    WHERE idSessao = %s
                )
            """,
            (id_conta, token_hash)
        )
        mydb.commit()
        return {"Sucesso": "Conta removida com sucesso!!"}
    except IntegrityError:
        mydb.rollback
    except DataError:
        mydb.rollback
    except OperationalError:
        mydb.rollback
    except DatabaseError:
        mydb.rollback
    finally:
        mycursor.close()
        mydb.close()

@privado.delete("/sairConta")
async def sair_conta(response: Response, nome_do_cookie: Annotated[str | None, Cookie(alias=NOME_COOKIE)] = None,):
    try:
        token_hash = hashlib.sha256(nome_do_cookie.encode()).hexdigest()
        mydb = connect.sqlConnection().Connection()
        mydb.connect()
        mycursor = mydb.cursor(buffered=True)

        mycursor.execute(
            """
                DELETE FROM sessao WHERE idSessao = %s
            """,
            (token_hash,)
        )

        mydb.commit()

        response.delete_cookie(
            key=NOME_COOKIE,
            path="/"
            )

        return {"Sucesso": "Sessao terminada com sucesso!"}
    except IntegrityError:
        mydb.rollback
    except OperationalError:
        mydb.rollback
    except DatabaseError:
        mydb.rollback
    finally:
        mycursor.close()
        mydb.close()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
    
app.include_router(publico)   # liga os routers à app
app.include_router(privado)