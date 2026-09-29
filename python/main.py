import mysql
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
import connect
from fastapi.middleware.cors import CORSMiddleware
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

app = FastAPI()

origins = [
    "http://localhost:5173",
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

        print(ph.hash(infRegistar.senha))

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
async def login(infLogin: Login):
    ph = PasswordHasher()
    mydb = connect.sqlConnection().Connection()
    mydb.connect()
    mycursor = mydb.cursor()

    perfilQuerry = "SELECT email FROM utilizadores WHERE email = %s"
    perfilValor = (infLogin.email)
    mycursor.execute(perfilQuerry, perfilValor)
    conta = mycursor.fetchone()

    try:
        ph.verify(perfilValor, conta[1])
        return {"Sucesso": "Login realizado com sucesso!"}
    except VerifyMismatchError:
        return {"Erro": "Senha incorreta!"}